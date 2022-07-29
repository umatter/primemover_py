from datetime import datetime
import pathlib
from src.worker.utilities import pref_as_dict
import pandas as pd
from src.worker import s3_wrapper
import src.worker.api_wrapper as api_wrapper
from src.worker.UpdateObject import UpdateObject

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

from src.base.BaseCrawler import BaseCrawler


def extract_data(experiment_id: int, api_credentials,
                 crawler_class=BaseCrawler):
    """
    Extract_data reads crawlers as seen in the file "resources/updates/generated.csv"

    input: str, path to json containing generated crawlers
    output: pandas DataFrame, columns all parameters set in the configuration functions
    """
    api_token = api_wrapper.get_access(api_credentials.get('username'),
                                       api_credentials.get('password'))

    crawler_list_raw = api_wrapper.fetch_experiment(access_token=api_token,
                                                    id=
                                                    experiment_id)

    crawler_list = crawler_class.from_list(crawler_list_raw['crawlers'])
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


def extract_list_params(object_name, experiment_id,api_credentials, crawler_class=BaseCrawler):
    """
    input:
        object_name: str, one of media or terms
    """
    api_token = api_wrapper.get_access(api_credentials.get('username'),
                                       api_credentials.get('password'))
    crawler_list_raw = api_wrapper.fetch_experiment(access_token=api_token,
                                                    id=
                                                    experiment_id)

    crawler_list = crawler_class.from_list(crawler_list_raw['crawlers'])
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


def setup_copy(experiment_id, api_credentials, date=datetime.now()):
    s3_wrapper.append_csv(f'config_{experiment_id}/single_params.csv',
                          extract_data(experiment_id, api_credentials))
    s3_wrapper.append_csv(f'config_{experiment_id}/terms.csv',
                          extract_list_params('terms', experiment_id, api_credentials))
    s3_wrapper.append_csv(f'config_{experiment_id}/media.csv',
                          extract_list_params('media', experiment_id, api_credentials))
    return "Success"
