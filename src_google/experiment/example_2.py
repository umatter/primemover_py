"""
Experiment partisan google elections 2022-01-03
This file generates new crawlers, in particular the required config files

J.L. 07.2022
"""
import os

from src.worker.TimeHandler import Schedule, TimeHandler
from src.worker import api_wrapper as api
from src.worker import s3_wrapper
from src_google.worker.classes import Crawler, Config, Proxy
from src_google.worker.config_functions import select_local_outlets
from src_google.worker import tasks

import json
from datetime import datetime, timedelta
import pathlib
import random as r

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

PATH_BENIGN_TERMS = PRIMEMOVER_PATH + '/resources/other/benign_terms.json'

PATH_OUTLETS = PRIMEMOVER_PATH + '/resources/input_data/outlets_pool.csv'
PATH_OUTLETS_LOCAL = PRIMEMOVER_PATH + '/resources/input_data/outlets_pool_local.csv'

GEOSURF_PATH = PRIMEMOVER_PATH + '/resources/proxies/geosurf_proxies.csv'


def launch_experiment(exp_id):
    # s3_wrapper.fetch_private("/resources/proxies/private_proxies.csv")
    # s3_wrapper.fetch_rotating("/resources/proxies/rotating_proxies.csv")
    s3_wrapper.fetch_geosurf()

    # s3_wrapper.update_valid_cities()

    s3_wrapper.fetch_neutral_domains()
    s3_wrapper.fetch_outlets()
    select_local_outlets(PATH_OUTLETS, PATH_OUTLETS_LOCAL, nr_per_state=1)

    # s3_wrapper.fetch_terms()
    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=10 * 60 * 60,
                                           end_at=(10 + 23) * 60 * 60,
                                           interval=600,
                                           )
    # Generate GEOSURF based crawlers
    GEO_SURF_PROXIES = ["US-CO-COLORADO_SPRINGS",
                        "US-OK-OKLAHOMA_CITY"]

    # generate neutral configurations
    config_list_neutral = [
        Config(name='CONFIGURATION_FUNCTIONS/neutral', location=l, pi=0,
               media=[], terms=[]) for
        l in 1 * GEO_SURF_PROXIES]
    # generate crawlers from neutral configs
    crawler_list = [
        Crawler(flag='neutral', configuration=c, experiment_id=exp_id) for
        c in
        config_list_neutral]
    # generate left and right configs with opposing pi in each location
    config_list_left = [Config(name='CONFIGURATION_FUNCTIONS/left', location=l)
                        for l in
                        1 * GEO_SURF_PROXIES]
    config_list_right = [
        Config(name='CONFIGURATION_FUNCTIONS/right',
               location=left_config.location,
               pi=-left_config.pi) for left_config in
        config_list_left]

    crawler_list += [
        Crawler(flag='left', configuration=c, experiment_id=exp_id) for c
        in
        config_list_left]
    crawler_list += [
        Crawler(flag='right', configuration=c, experiment_id=exp_id) for c
        in
        config_list_right]


    # Set privacy
    with_privacy = r.sample(crawler_list, k=2)
    for i, crawler in enumerate(with_privacy):
        if i < 20:
            crawler.agent.multilogin_profile.geolocation = 'BLOCK'
        elif i < 40:
            crawler.agent.multilogin_profile.do_not_track = 1
        elif i < 60:
            crawler.agent.multilogin_profile.hardware_canvas = "BLOCK"
        elif i < 80:
            crawler.agent.multilogin_profile.local_storage = False
            crawler.agent.multilogin_profile.service_worker_cache = False

    [c.add_task(tasks.GoogleSearch_new, params={'term': "Watts Occurring?"}) for c in crawler_list]

    queues = [c.queues[0] for c in crawler_list]
    queues.sort(key=lambda qu: datetime.fromisoformat(qu.start_at))
    t_0 = datetime.now() + timedelta(minutes=1)
    print(t_0)
    delta_t_1 = int(120)
    for q in queues[0:]:
        q.start_at = t_0.isoformat()
        t_0 += timedelta(seconds=delta_t_1)

    if not os.path.isdir(PRIMEMOVER_PATH + '/resources/crawlers'):
        os.mkdir(PRIMEMOVER_PATH + '/resources/crawlers')
    with open(PRIMEMOVER_PATH + "/resources/examples/example_new_crawlers.json",
              'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return f"exp_id = {exp_id}"


if __name__ == "__main__":
    with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
        KEYS = json.load(f)

    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    launch_experiment(exp_id=49)
