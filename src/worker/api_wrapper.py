import requests
import json
from datetime import datetime
import gzip
import os
import io
import zipfile

DOMAIN = "https://siaw.qlick.ch/api/v1/"


def push_new(path='resources/examples/test_crawler_py.json'):
    with open(path, 'r') as f:
        data_crawlers = json.load(f)
    post_crawlers = requests.post(DOMAIN + 'load', json=data_crawlers)
    return post_crawlers


def fetch_results(
        path=f'resources/raw_data/{datetime.today().date().isoformat()}.json'):
    if os.path.exists(path):
        raise Exception('file already exists')
    raw_data = requests.get(DOMAIN + 'queues-unreviewed')
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')


def fetch_reviewed(
        path=f'resources/raw_data/reviewed_{datetime.today().date().isoformat()}.json'):
    if os.path.exists(path):
        raise Exception('file already exists')
    raw_data = requests.get(DOMAIN + 'queues-reviewed')
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')


def fetch_all_crawlers(
        path=f'resources/crawlers/{datetime.today().date().isoformat()}.json'):
    raw_data = requests.get(DOMAIN + 'crawlers')
    raw_dict = raw_data.json()
    with open(path, 'w') as f:
        json.dump(raw_dict, f, indent='  ')


def fetch_html(url):
    print(url)
    r = requests.get(url)
    zipdata = io.BytesIO(r.content)
    as_zipfile = zipfile.ZipFile(zipdata)
    name = None
    for name in as_zipfile.namelist():
        if 'html' in name:
            break
    raw_html = as_zipfile.read(name)

    return raw_html


def set_reviewed(queue_id):
    r = requests.put(DOMAIN + f'queues/{queue_id}', data={'reviewed': 1})
    if r.status_code == 200:
        return 'success'
    else:
        raise ConnectionError(f'status code {r.status_code}')


def get_outlets():
    r = requests.get(DOMAIN + 'outlets')
    return r.json()['data']


def get_terms():
    r = requests.get(DOMAIN + 'terms')
    return r.json()['data']
