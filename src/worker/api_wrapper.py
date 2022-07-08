"""
Wrapper functions for the primemover api.

Available Functions:
    - push_new: Wrapper for the primemover load function
    - fetch_results: Wrapper for the queues-unreviewed method of the primemover api
    - fetch_reviewed: Wrapper for the queues-reviewed method of the primemover api
    - fetch_unprocessed: Wrapper for the queues-unprocessed method of the primemover api
    - fetch_all_crawlers: Wrapper for the crawlers method of the primemover api. This contains all active crawlers.
    - set_reviewed: Set queue reviewed flag to 1
    - get_outlets: Fetch all outlets from primemover_api
    - get_terms: Fetch all terms from primemover_api

J.L. 11.2020
"""

import requests
import json
from datetime import datetime
import os

import pathlib
from src.worker.Experiment import Experiment

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

DOMAIN = "https://primemoverswitch.wimando.ch/api/v1/"


def get_access(e_mail, password):
    """
    Wrapper for the primemover login function. Use to post json like data from path.

    Returns:
        bearer Token (access_token)
    """
    try:
        params = {'email': e_mail, 'password': password}
        post_login = requests.post(DOMAIN + 'login', params=params)
        returned = post_login.json()
        token = returned['access_token']
    except:
        token = ""
        Warning("Could not login to api")

    return token


def push_new(access_token,
             path=PRIMEMOVER_PATH + '/resources/examples/test_crawler_py.json'):
    """
    Wrapper for the primemover load function. Use to post json like data from path.
    Args:
        access_token: bearer Token
        path: valid path to a json document
    Returns:
        response from primemover api
    """
    with open(path, 'r') as f:
        data_crawlers = json.load(f)
    post_crawlers = requests.post(DOMAIN + 'load', json=data_crawlers, headers={
        'authorization': 'Bearer ' + access_token})

    return post_crawlers


def fetch_results(access_token,
                  experiment_id=None,
                  path=f'{PRIMEMOVER_PATH}/resources/raw_data/{datetime.today().date().isoformat()}.json'):
    """
    Wrapper for the queues-unreviewed method of the primemover api. These are all
    processed, unreviewed queues.

    Args:
        experiment_id: int, id of an existing experiment
        access_token: str, bearer Token
        path: target path where response json will be stored, raises an error if path already exists.
            default: resources/raw_data/<<Today's Date>>.json'
    Returns:
        dictionary response from api
    """
    if os.path.exists(path):
        raise FileExistsError('file already exists')
    if experiment_id is not None:
        raw_data = requests.get(
            DOMAIN + f'experiments/{experiment_id}/queues-unreviewed',
            headers={
                'authorization': 'Bearer ' + access_token})
    else:
        raw_data = requests.get(DOMAIN + 'queues-unreviewed',
                                headers={
                                    'authorization': 'Bearer ' + access_token})
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')
    return raw_dict


def fetch_reviewed(access_token,
                   path=f'{PRIMEMOVER_PATH}/resources/raw_data/reviewed_{datetime.today().date().isoformat()}.json'):
    """
    Wrapper for the queues-reviewed method of the primemover api. This contains all previously
        reviewed queues (reviewed is not set automaticaly, use set_reviewed())
    Args:
        access_token: str, bearer Token
        path: target path where response json will be stored, raises an error if path already exists.
            default: resources/raw_data/reviewed_<<Today's Date>>.json'
    Returns:
        dictionary response from api
    """
    if os.path.exists(path):
        raise Exception('file already exists')
    raw_data = requests.get(DOMAIN + 'queues-reviewed',
                            headers={'authorization': f'Bearer {access_token}'})
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')
    return raw_dict


def fetch_unprocessed(access_token,
                      path=f'{PRIMEMOVER_PATH}/resources/raw_data/unprocessed_{datetime.today().date().isoformat()}.json'):
    """
    Wrapper for the queues-unprocessed method of the primemover api. This contains all queues not
        yet processed by the runner. This includes inactive queues.
    Args:
        access_token: str, bearer Token
        path: target path where response json will be stored, raises an error if path already exists.
            default: resources/raw_data/unprocessed_<<Today's Date>>.json'
    Returns:
        dictionary response from api
    """
    if os.path.exists(path):
        raise Exception('file already exists')
    raw_data = requests.get(DOMAIN + 'queues-unprocessed',
                            headers={'authorization': f'Bearer {access_token}'})
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')
    return raw_dict


def fetch_all_crawlers(access_token,
                       path=f'{PRIMEMOVER_PATH}/resources/crawlers/{datetime.today().date().isoformat()}.json'):
    """
    Wrapper for the crawlers method of the primemover api. This contains all active crawlers.

    Args:
        access_token: str, bearer Token
        path: target path where response json will be stored. Existing data is overwritten!
            default: resources/crawlers/<<Today's Date>>.json'
    Returns:
        dictionary response from api
    """
    raw_data = requests.get(DOMAIN + 'crawlers',
                            headers={'authorization': f'Bearer {access_token}'})
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')
    return raw_dict


def set_reviewed(access_token, queue_id: int):
    """
    Wrapper function to set queue status to reviewed.
    Args:
        access_token: str, bearer Token
        queue_id: The id of a queue that is to be set to reviewed
    Returns:
        'sucess' if status code 200, else raises ConnectionError with response status code
    """
    r = requests.put(DOMAIN + f'queues/{queue_id}', data={'reviewed': 1},
                     headers={'authorization': f'Bearer {access_token}'})
    if r.status_code == 200:
        return 'success'
    else:
        raise ConnectionError(f'status code {r.status_code}')


def set_inactive(access_token, queue_id):
    """
    Wrapper function set queue status to active = 0
    Args:
        access_token: str, bearer Token
        queue_id: The id of a queue that is to be set to reviewed
    Returns:
        'sucess' if status code 200, else raises ConnectionError with response status code
    """
    r = requests.put(DOMAIN + f'queues/{queue_id}', data={'active': 0},
                     headers={'authorization': f'Bearer {access_token}'})
    if r.status_code in {200, 404}:
        return 'success'
    else:
        raise ConnectionError(f'status code {r.status_code}')


def new_experiment(access_token, experiment):
    """
    Wrapper function to create a new experiment object
    Args:
        access_token: str, bearer Token
        experiment: dict, expeiment to create, must be in valid format (see base.BaseExperient)
    Returns:
        contents of response json at key 'data'
    """
    r = requests.post(DOMAIN + 'experiments',
                      headers={'authorization': f'Bearer {access_token}'},
                      json=experiment)
    return r.json()['data']


def update_experiment(access_token, experiment, exp_id):
    """
    Wrapper function to upaate an experiment object
    Args:
        access_token: str, bearer Token
        experiment: dict, matching experiment format
        exp_id: int, id of experiment to update
    Returns:
        contents of response json at key 'data'
    """
    r = requests.put(DOMAIN + f'experiments/{exp_id}',
                     headers={'authorization': f'Bearer {access_token}'},
                     json=experiment)
    return r.json()['data']


def fetch_experiment(access_token, id):
    """
    Wrapper function to fetch an existing experiment object
    Returns:
        contents of response json at key 'data'
    """
    r = requests.get(DOMAIN + f'experiments/{id}',
                     headers={'authorization': f'Bearer {access_token}'})
    return r.json()['data']


def fetch_all_experiments(access_token):
    """
    Wrapper function to fetch an existing experiment object
    Returns:
        contents of response json at key 'data'
    """
    r = requests.get(DOMAIN + f'experiments',
                     headers={'authorization': f'Bearer {access_token}'})
    return r.json()['data']


def fetch_agent(id):
    r = requests.get(DOMAIN + f'agents/{id}')
    return r.json()['data']


def fetch_crawler(id):
    r = requests.get(DOMAIN + f'crawlers/{id}')
    return r.json()['data']


def fetch_queue(id):
    r = requests.get(DOMAIN + f'queues/{id}')
    return r.json()['data']


def fetch_proxy(id):
    r = requests.get(DOMAIN + f'proxies/{id}')
    return r.json()['data']


def fetch_config(id):
    r = requests.get(DOMAIN + f'configurations/{id}')
    return r.json()['data']


def fetch_crawlers_by_exp(access_token, experiment_id):
    exp = fetch_experiment(access_token, experiment_id)
    exp = Experiment.from_dict(exp)
    crawler_list = []
    for c in exp.crawler_ids:
        try:
            crawler_list.append(c)
        except:
            return Exception(f'Crawler id was {c}')
    return crawler_list


def delete_exp(access_token, id):
    requests.delete(DOMAIN + f'experiments/{id}',
                    headers={'authorization': f'Bearer {access_token}'})


def delete_queues_2(access_token, i):
    resp = requests.delete(DOMAIN + f'queues/{i}',
                           headers={'authorization': f'Bearer {access_token}'})
    return resp
