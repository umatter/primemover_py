"""
Experiment partisan google elections 2020-10-21
This file generates new crawlers, in particular the required config files

J.L. 11.2020
"""
from src.worker.Crawler import Crawler
from src.worker.TimeHandler import Schedule, TimeHandler
from src.Configuration.ConfigureProfile import Config
from src.worker import api_wrapper as api
import json
from datetime import datetime

PATH_TERMS = {
    'instagram': "resources/input_data/insta_top_partisan_hashtags.csv",
    'bigrams': "resources/input_data/most_partisan_searchterms_pool.csv"}
PATH_MEDIA_OUTLETS = "resources/input_data/twitter_stream_top_partisan_domains.csv"
PATH_BENIGN_TERMS = 'resources/other/benign_terms.json'

with open("resources/other/partisan_election_hometowns.json", 'r') as file:
    LOCATION_LIST = json.load(file)

if __name__ == "__main__":

    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=10 * 60 * 60,
                                           end_at=(10 + 23) * 60 * 60,
                                           interval=600,
                                           )

    # generate neutral crawlers
    config_list_neutral = [
        Config(name='Config/neutral', location=l, pi=0, media={}, terms={}) for
        l in 2 * LOCATION_LIST]
    crawler_list_neutral = [Crawler(flag='neutral', configuration=c, experiment_id=2) for c in
                            config_list_neutral]

    # generate left wing crawlers
    config_list_left = [Config(name='Config/left',
                               location=l, pi=-1)
                        for l in 2 * LOCATION_LIST]

    crawler_list_political = [Crawler(flag='left', configuration=c, experiment_id=2) for c in
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
    with open("resources/election_experiment/election_crawler_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(path="resources/election_experiment/election_crawler_py.json")
    data_as_dict = json.loads(return_data.text)

    with open(
            f'resources/crawlers/exp_2_{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')
