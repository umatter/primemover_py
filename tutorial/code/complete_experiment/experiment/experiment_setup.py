# Classes are now imported from our worker/classes file
from tutorial.code.more_complete_setup.worker.classes import Crawler, Config, \
    Proxy

# We will start with a browser leaks queue, so lets load the base tasks
from src.base import base_tasks as tasks

from src.worker import s3_wrapper
from src.worker.TimeHandler import TimeHandler, Schedule
from src.worker import api_wrapper as api
from datetime import datetime, timedelta
from src.worker.Experiment import Experiment

import os
import json
import pathlib
import random as r
PRIMEMOVER_PATH = str(
    pathlib.Path(__file__).parent.parent.parent.parent.parent.absolute())


def launch_experiment(api_token, update_files=False, push=True):
    """
    Param:
        update_files, Bool: If False, first_crawler will not attempt to fetch valid_cities, outlets and terms from s3
        push, Bool: if False, no new experiment will be created and no queues will be pushed
    """
    if update_files:
        s3_wrapper.update_valid_cities()
        s3_wrapper.fetch_outlets()
        s3_wrapper.fetch_terms()

    exp = Experiment(
        name='Test Experiment',
        description='A first step towards using primemover_py',
        contact='you',
    )
    if push :
        exp_return = api.new_experiment(api_token, exp.as_dict())
        exp_id = Experiment.from_dict(exp_return).id
    else:
        exp_id = 0

    first_config = Config(location='US-AZ-PHOENIX')

    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)

    GEO_SURF_PROXIES = ["US-CA-OAKLAND",
                        "US-CA-OAKLAND"]
    # generate neutral configurations
    # Giving a configuration a name <Name>/<text> assigns the configuration the flag <text>. This can then be used for configuring or assigning
    # different tasks
    config_list_neutral = [
        Config(name='Config/neutral', location=l, pi=0) for
        l in 2 * GEO_SURF_PROXIES]
    # generate crawlers from neutral configs
    # the flag for the crawler is automatically taken from config, the assignment here is therefore redundant.
    crawler_list = [
        Crawler(flag='neutral', configuration=c, experiment_id=exp_id) for
        c in
        config_list_neutral]
    # generate left and right configs with opposing pi in each location
    config_list_left = [
        Config(name='Config', location=l, flag='left')
        for l in
        3 * GEO_SURF_PROXIES]
    config_list_right = [
        Config(name='Config',
               location=left_config.location,
               pi=-left_config.pi) for left_config in
        config_list_left]

    # Make Crawlers from the left and right config lists
    crawler_list += [
        Crawler(configuration=c, experiment_id=exp_id) for c
        in
        config_list_right + config_list_left]

    # Assign some crawlers different privacy settings retroactively
    with_privacy = r.sample(crawler_list, k=20)
    for i, crawler in enumerate(with_privacy):
        if i < 3:
            crawler.agent.multilogin_profile.geolocation = 'BLOCK'
        elif i < 6:
            crawler.agent.multilogin_profile.do_not_track = 1
        elif i < 9:
            crawler.agent.multilogin_profile.hardware_canvas = "BLOCK"
        elif i < 12:
            crawler.agent.multilogin_profile.local_storage = False
            crawler.agent.multilogin_profile.service_worker_cache = False


    if not os.path.isdir(PRIMEMOVER_PATH + '/resources/crawlers'):
        os.mkdir(PRIMEMOVER_PATH + '/resources/crawlers')
    with open(PRIMEMOVER_PATH + "/resources/crawlers/experiment_3.json",
              'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')
    if push:
        return_data = api.push_new(access_token=api_token,
                                   path=PRIMEMOVER_PATH + "/resources/crawlers/experiment_3.json")
        data_as_dict = json.loads(return_data.text)

        with open(
                PRIMEMOVER_PATH + "/resources/crawlers/more_complete_setup.json",
                'w') as file:
            json.dump([crawler.as_dict() for crawler in crawler_list], file,
                      indent='  ')

    return exp_id


if __name__ == "__main__":
    with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
        KEYS = json.load(f)
    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    launch_experiment(key, False, True)
