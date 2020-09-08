import requests
DOMAIN = "https://siaw.qlick.ch/"
import json
#login
    # fetch user info from non git file
    # post request (always do on startup)
    # set tau

#logout
    # logout, always do on exit

# fetch existing bots?
resp_crawlers = requests.get(DOMAIN+'api/v1/crawlers/')
data_crawlers = json.loads(resp_crawlers.text)

resp_config = requests.get(DOMAIN+'api/v1/configurations/')
data_config = json.loads(resp_config.text)

data_behaviours = requests.get(DOMAIN+'api/v1/behaviors/')
data_behaviours = json.loads(data_behaviours.text)
# temporary: fetch example from resources/examples
with open('resources/examples/crawlers.json', 'r') as f:
    data_crawlers = json.load(f)

with open('resources/examples/configurations_extended.json', 'r') as f:
    data_configs = json.load(f)



# push local bot config to api



