import requests
import json

DOMAIN = "https://siaw.qlick.ch/"

with open('resources/examples/example_crawler_py.json', 'r') as f:
    data_crawlers = json.load(f)

resp_crawlers = requests.post(DOMAIN + 'api/v1/load', json=data_crawlers[1:])


