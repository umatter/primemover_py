from src.worker.Crawler import Crawler
from datetime import datetime, timedelta
import json
import pathlib
from src.worker.Utilities import pref_as_dict
import pandas as pd
from src.worker import s3_wrapper
import src.auxiliary.result_select as result_select
import src.worker.api_wrapper as api_wrapper
from src.worker.UpdateObject import UpdateObject

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)

ACCESS_TOKEN = api_wrapper.get_access(KEYS['PRIMEMOVER']['username'],
                                      KEYS['PRIMEMOVER']['password'])


def extract_data(experiment_id: int):
    """
    Extract_data reads crawlers as seen in the file "resources/updates/generated.csv"

    input: str, path to json containing generated crawlers
    output: pandas DataFrame, columns all parameters set in the configuration functions
    """

    crawler_list_raw = api_wrapper.fetch_experiment(access_token=ACCESS_TOKEN,
                                                    id=
                                                    experiment_id)

    crawler_list = Crawler.from_list(crawler_list_raw['crawlers'])
    crawler_list = UpdateObject(crawler_list, 'config')

    data_restructure = []
    date = datetime.today().date().isoformat()
    for c in crawler_list:
        new_row = {'date_time': date, 'flag': c.flag}
        if c.crawler_info is not None:
            new_row['crawler_id'] = c.crawler_info.crawler_id
        else:
            new_row['crawler_id'] = None
        new_row['crawler_name'] = c.name

        config_dict = c.configuration.as_dict()
        pref = pref_as_dict(config_dict.get('preferences', []))
        parameter_dict = config_dict.get('params', [{}])[0]
        parameter_dict.update(pref)

        for parameter, value in parameter_dict.items():
            if isinstance(value, (int, float, str)):
                new_row[parameter] = value
        data_restructure.append(new_row)
    return pd.DataFrame(data=data_restructure)


def extract_list_params(object_name, experiment_id):
    """
    input:
        object_name: str, one of media or terms
    """
    crawler_list_raw = api_wrapper.fetch_experiment(access_token=ACCESS_TOKEN,
                                                    id=
                                                    experiment_id)

    crawler_list = Crawler.from_list(crawler_list_raw['crawlers'])
    crawler_list = UpdateObject(crawler_list, 'config')

    data_restructure = []
    date = datetime.today().date().isoformat()
    for c in crawler_list:
        base_row = {'date_time': date, 'flag': c.flag}
        if c.crawler_info is not None:
            base_row['crawler_id'] = c.crawler_info.crawler_id
        else:
            base_row['crawler_id'] = None
        base_row['crawler_name'] = c.name
        config = c.configuration
        if object_name == 'media':
            list_object = config.media
        elif object_name == 'terms':
            list_object = config.terms
        else:
            raise ValueError('can currently only parse terms and media')
        for dict_object in list_object:
            new_row = base_row.copy()
            new_row.update(dict_object)
            data_restructure.append(new_row)
    return pd.DataFrame(data=data_restructure)


def extract_selection_data(experiment_id, path_cleaned_data):
    # Run with results, not after update!!! Relevant parameters will otherwhise be different.
    path_jobs = f'{PRIMEMOVER_PATH}/{path_cleaned_data}'
    with open(path_jobs) as f:
        raw_data = json.load(f)

    crawler_list_raw = api_wrapper.fetch_experiment(access_token=ACCESS_TOKEN,
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
                        alpha_tilde=new_row['pi'],
                        tau_tilde=new_row['tau'],
                        beta_i=new_row['beta'])
                else:
                    u_py = result_select.result_utility_w_i_j_t(new_row['rank'],
                                                                new_row['beta'])

                new_row.update({'u_py': u_py})
                data_restructure.append(new_row)
        data_df = pd.DataFrame(data=data_restructure)
        data_df['difference'] = data_df['u_py'] - data_df['u_raw']
        data_df['correct'] = abs(data_df['difference'] < 10 ** -5)

    return data_df


def create_copy(experiment_id, date=datetime.now()):
    date = date.date().isoformat()
    s3_wrapper.append_csv(f'config_{experiment_id}/single_params.csv',
                          extract_data(experiment_id))
    s3_wrapper.append_csv(f'config_{experiment_id}/terms.csv',
                          extract_list_params('terms', experiment_id))
    s3_wrapper.append_csv(f'config_{experiment_id}/media.csv',
                          extract_list_params('media', experiment_id))
    selection_data = extract_selection_data(experiment_id,
                                            f'resources/cleaned_data/{date}.json')
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


if __name__ == "__main__":
    s3_wrapper.append_csv(f'selected_{22}/selections.csv',
                          extract_selection_data(22,
                                                 f'resources/cleaned_data/{"2021-06-07"}.json'))
