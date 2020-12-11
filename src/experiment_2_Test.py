"""
Experiment partisan google elections 2020-10-21
This file generates new crawlers, in particular the required config files

J.L. 11.2020
"""
from src.worker.Crawler import Crawler
from src.worker.TimeHandler import Schedule, TimeHandler
from src.worker.ConfigureProfile import Config
from src.worker import api_wrapper as api
import json
import time
from datetime import datetime
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())


PATH_BENIGN_TERMS = PRIMEMOVER_PATH + '/resources/other/benign_terms.json'

with open(PRIMEMOVER_PATH + "/resources/other/partisan_election_hometowns.json", 'r') as file:
    LOCATION_LIST = json.load(file)[0:2]

if __name__ == "__main__":

    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=10 * 60 * 60,
                                           end_at=(10 + 23) * 60 * 60,
                                           interval=600,
                                           )

    # generate neutral crawlers
    config_list_neutral = [
        Config(name='Config/neutral', location=l, pi=0, media="", terms="") for
        l in  LOCATION_LIST]
    crawler_list_neutral = [Crawler(flag='neutral', configuration=c, experiment_id=1) for c in
                            config_list_neutral]

    # generate left wing crawlers
    config_list_left = [Config(name='Config/left',
                               location=l)
                        for l in LOCATION_LIST]

    crawler_list_political = [Crawler(flag='left', configuration=c, experiment_id=1) for c in
                              config_list_left]

    # generate right wing crawlers
    config_list_right = [
        Config(name='Config/right',
               location=left_config.location,
               pi=- left_config.pi)
        for left_config in config_list_left]
    crawler_list_political += [Crawler(flag='right', configuration=c, experiment_id=2) for c in
                               config_list_right]

    crawler_list = crawler_list_neutral + crawler_list_political
    with open(PRIMEMOVER_PATH + "/resources/crawlers/test_1.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list][4:5], file,
                  indent='  ')
    key = api.get_access('p@wimando.ch', 'And#Qom5F20')
    return_data = api.push_new(access_token=key, path=PRIMEMOVER_PATH + "/resources/crawlers/test_1.json")
    data_as_dict = json.loads(return_data.text)

    with open(
            f'{PRIMEMOVER_PATH}/resources/crawlers/test_1_{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')
