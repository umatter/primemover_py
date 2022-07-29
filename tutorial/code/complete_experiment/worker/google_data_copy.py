from src_google.worker.classes import Crawler

import json
import src.auxiliary.result_select as result_select
from src.base.DataCopy import *
from src.worker.UpdateObject import UpdateObject

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)


def extract_selection_data(experiment_id, api_credentials, path_cleaned_data):
    # Run with results, not after update!!! Relevant parameters will otherwise be different.

    api_token = api_wrapper.get_access(api_credentials.get('username'),
                                       api_credentials.get('password'))

    path_jobs = f'{PRIMEMOVER_PATH}/{path_cleaned_data}'
    with open(path_jobs) as file:
        raw_data = json.load(file)

    crawler_list_raw = api_wrapper.fetch_experiment(access_token=api_token,
                                                    id=
                                                    experiment_id)

    crawler_list = Crawler.from_list(crawler_list_raw['crawlers'])
    crawler_list = UpdateObject(crawler_list, 'config')

    crawler_data_dict = {}
    for c in crawler_list:
        c_id = c.crawler_info.crawler_id
        c_dict = {'name': c.name,
                  'beta': c.configuration.beta,
                  'alpha': c.configuration.alpha,
                  'pi': c.configuration.pi,
                  'tau': c.configuration.tau}
        crawler_data_dict[c_id] = c_dict

    data_restructure = []
    for crawler_id, jobs in raw_data.items():
        crawler_id = int(crawler_id)
        base_row = {'crawler_id': crawler_id}

        if (crawler_params := crawler_data_dict.get(crawler_id, None)) is None:
            continue
        else:
            base_row.update(crawler_params)
        for job in jobs:
            job_id = job.get('job_id')
            base_row_2 = base_row.copy()
            base_row_2.update(
                {"job_id": job_id, "finished_at": job['finished_at']})
            response_data, success = s3_wrapper.download_dynamic(job_id)
            if not success:
                continue
            for result in response_data.get('items'):
                new_row = base_row_2.copy()
                new_row.update(result)
                outlet = new_row.pop('outlet')
                if new_row['known']:
                    known = 1
                    if outlet['pi'] is None:
                        known = 0
                        d_tilde_i_j_t = 0
                    else:
                        d_tilde_i_j_t = abs(new_row['pi'] - float(outlet['pi']))
                    u_py = result_select.result_utility_w_i_j_t(
                        r_j=new_row['rank'],
                        known=known,
                        d_tilde_i_j_t=d_tilde_i_j_t,
                        alpha_tilde=new_row['alpha'],
                        tau_tilde=new_row['tau'],
                        beta_i=new_row['beta'])
                else:
                    u_py = result_select.result_utility_w_i_j_t(new_row['rank'],
                                                                new_row['beta'])

                new_row.update({'u_py': u_py})
                data_restructure.append(new_row)

        data_df = pd.DataFrame(data=data_restructure)
        if 'u_py' not in data_df.columns:
            data_df['u_py'] = ''
        if 'u_raw' not in data_df.columns:
            data_df['u_raw'] = ''
        data_df['difference'] = data_df['u_py'] - data_df['u_raw']
        data_df['correct'] = abs(data_df['difference'] < 10 ** -5)

    return data_df


def create_copy(experiment_id, api_credentials, date=datetime.now().date()):
    date = date.isoformat()
    s3_wrapper.append_csv(f'config_{experiment_id}/single_params.csv',
                          extract_data(experiment_id, api_credentials))
    s3_wrapper.append_csv(f'config_{experiment_id}/terms.csv',
                          extract_list_params('terms', experiment_id, api_credentials))
    s3_wrapper.append_csv(f'config_{experiment_id}/media.csv',
                          extract_list_params('media', experiment_id, api_credentials))
    selection_data = extract_selection_data(experiment_id, api_credentials,
                                            f'resources/cleaned_data/{date}.json')
    if len(selection_data) > 0:
        s3_wrapper.append_csv(f'selected_{experiment_id}/selections.csv',
                              selection_data)
    mistakes = selection_data.loc[-selection_data['correct']]

    try:
        with open(
                PRIMEMOVER_PATH + f'/resources/log/log_{date}.json',
                'r') as f:
            log = json.load(f)
    except FileNotFoundError:
        log = {"Tasks": {}}
    with open(PRIMEMOVER_PATH + f'/resources/log/log_{date}.json',
              'w') as f:
        log["Tasks"][f'Data Copy'] = "success"
        log["Selection Errors"] = len(mistakes)
        json.dump(log, f, indent='  ')
    if len(mistakes) > 0:
        mistakes.to_csv(
            PRIMEMOVER_PATH + f'/resources/log/calc_errors_log_{date}.csv')
    return 'Success'
