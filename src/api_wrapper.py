import requests
import json

DOMAIN = "https://siaw.qlick.ch/"


def push_new(path='resources/examples/test_crawler_py.json'):
    with open(path, 'r') as f:
        data_crawlers = json.load(f)
    post_crawlers = requests.post(DOMAIN + 'api/v1/load', json=data_crawlers)
    return post_crawlers
