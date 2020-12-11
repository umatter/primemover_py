"""
Wrapper functions for the primemover api.

Available Functions:
    - push_new: Wrapper for the primemover load function
    - fetch_results: Wrapper for the queues-unreviewed method of the primemover api
    - fetch_reviewed: Wrapper for the queues-reviewed method of the primemover api
    - fetch_unprocessed: Wrapper for the queues-unprocessed method of the primemover api
    - fetch_all_crawlers: Wrapper for the crawlers method of the primemover api. This contains all active crawlers.
    - fetch_html: Fetch html files from single report
    - set_reviewed: Set queue reviewed flag to 1
    - get_outlets: Fetch all outlets from primemover_api
    - get_terms: Fetch all terms from primemover_api

J.L. 11.2020
"""
import requests
from requests_oauthlib import OAuth2Session
import json
from datetime import datetime
import os
import io
import zipfile
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())
DOMAIN = " https://primemover.wimando.ch/api/v1/"


def get_access(e_mail, password):
    """
    Wrapper for the primemover login function. Use to post json like data from path.

    Returns:
        access_token
    """

    params = {'email': e_mail, 'password': password}
    post_login = requests.post(DOMAIN + 'login', params=params)
    return post_login.json()['access_token']


def push_new(access_token,
             path=PRIMEMOVER_PATH + '/resources/examples/test_crawler_py.json'):
    """
    Wrapper for the primemover load function. Use to post json like data from path.
    Args:
        path: valid path to a json document
    Returns:
        response from primemover api
    """
    with open(path, 'r') as f:
        data_crawlers = json.load(f)
    post_crawlers = requests.post(DOMAIN + 'load', json=data_crawlers, headers={
        'Authorization': 'Bearer ' + access_token})

    return post_crawlers


def fetch_results(access_token,
                  path=f'{PRIMEMOVER_PATH}/resources/raw_data/{datetime.today().date().isoformat()}.json'):
    """
    Wrapper for the queues-unreviewed method of the primemover api. These are all
    processed, unreviewed queues.

    Args:
        path: target path where response json will be stored, raises an error if path already exists.
            default: resources/raw_data/<<Today's Date>>.json'
    Returns:
        dictionary response from api
    """
    if os.path.exists(path):
        raise Exception('file already exists')
    raw_data = requests.get(DOMAIN + 'queues-unreviewed',
                            headers={'Authorization': 'Bearer ' + access_token})
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
        path: target path where response json will be stored, raises an error if path already exists.
            default: resources/raw_data/reviewed_<<Today's Date>>.json'
    Returns:
        dictionary response from api
    """
    if os.path.exists(path):
        raise Exception('file already exists')
    raw_data = requests.get(DOMAIN + 'queues-reviewed',
                            headers={'Authorization': f'Bearer {access_token}'})
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
        path: target path where response json will be stored, raises an error if path already exists.
            default: resources/raw_data/unprocessed_<<Today's Date>>.json'
    Returns:
        dictionary response from api
    """
    if os.path.exists(path):
        raise Exception('file already exists')
    raw_data = requests.get(DOMAIN + 'queues-unprocessed',
                            headers={'Authorization': f'Bearer {access_token}'})
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')
    return raw_dict


def fetch_all_crawlers(access_token,
                       path=f'{PRIMEMOVER_PATH}/resources/crawlers/{datetime.today().date().isoformat()}.json'):
    """
    Wrapper for the crawlers method of the primemover api. This contains all active crawlers.

    Args:
        path: target path where response json will be stored. Existing data is overwritten!
            default: resources/crawlers/<<Today's Date>>.json'
    Returns:
        dictionary response from api
    """
    raw_data = requests.get(DOMAIN + 'crawlers',
                            headers={'Authorization': f'Bearer {access_token}'})
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')
    return raw_dict


def fetch_html(access_token, url):
    """
    Wrapper function to fetch html data from report urls
    Args:
        url: A url to a report file, e.g. "https://siaw.qlick.ch/api/v1/file/227989"
    Returns:
        html as text
    """
    r = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
    zipdata = io.BytesIO(r.content)
    as_zipfile = zipfile.ZipFile(zipdata)
    name = None
    for name in as_zipfile.namelist():
        if 'html' in name:
            break
    raw_html = as_zipfile.read(name)

    return raw_html


def set_reviewed(access_token, queue_id: int):
    """
    Wrapper function to set queue status to reviewed.
    Args:
        queue_id: The id of a queue that is to be set to reviewed
    Returns:
        'sucess' if status code 200, else raises ConnectionError with response status code
    """
    r = requests.put(DOMAIN + f'queues/{queue_id}', data={'reviewed': 1},
                     headers={'Authorization': f'Bearer {access_token}'})
    if r.status_code == 200:
        return 'success'
    else:
        raise ConnectionError(f'status code {r.status_code}')


def set_inactive(access_token, queue_id):
    """
    Wrapper function set queue status to active = 0
    Args:
        queue_id: The id of a queue that is to be set to reviewed
    Returns:
        'sucess' if status code 200, else raises ConnectionError with response status code
    """
    r = requests.put(DOMAIN + f'queues/{queue_id}', data={'active': 0},
                     headers={'Authorization': f'Bearer {access_token}'})
    if r.status_code == 200:
        return 'success'
    else:
        raise ConnectionError(f'status code {r.status_code}')


def get_outlets(access_token):
    """
    Wrapper function to retrive media outlets from primemover api
    Returns:
        contents of response json at key 'data'
    """
    r = requests.get(DOMAIN + 'outlets',
                     headers={'Authorization': f'Bearer {access_token}'})
    return r.json()['data']


def get_terms(access_token):
    """
    Wrapper function to retrive search terms from primemover api
    Returns:
        contents of response json at key 'data'
    """
    r = requests.get(DOMAIN + 'terms',
                     headers={'Authorization': f'Bearer {access_token}'})
    return r
