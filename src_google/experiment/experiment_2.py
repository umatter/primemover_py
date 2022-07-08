"""
Experiment partisan google elections 2022-01-03
This file generates new crawlers, in particular the required config files

J.L. 07.2022
"""
import os

from src.worker.TimeHandler import Schedule, TimeHandler
from src.worker import api_wrapper as api
from src.worker import s3_wrapper
from src.worker.Experiment import Experiment

from src_google.worker.classes import Crawler, Config, Proxy
from src_google.worker.config_functions import select_local_outlets

import json
from datetime import datetime
import pathlib
import random as r

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

PATH_BENIGN_TERMS = PRIMEMOVER_PATH + '/resources/other/benign_terms.json'

ROTATING_PATH = PRIMEMOVER_PATH + '/resources/proxies/rotating_proxies.csv'

PRIVATE_PATH = PRIMEMOVER_PATH + '/resources/proxies/private_proxies.csv'

PATH_OUTLETS = PRIMEMOVER_PATH + '/resources/input_data/outlets_pool.csv'
PATH_OUTLETS_LOCAL = PRIMEMOVER_PATH + '/resources/input_data/outlets_pool_local.csv'

GEOSURF_PATH = PRIMEMOVER_PATH + '/resources/proxies/geosurf_proxies.csv'


def distribute_proxies(location_groups, exp_id, proxy_credentials,
                       proxy_type="rotating"):
    crawler_list = []
    for single_location in location_groups:
        pi_left = None
        pi_right = None
        location = single_location[0]
        single_location = single_location[1].reset_index(drop=True)
        shift = r.sample([0, 1], 2)
        for idx in single_location.index:
            if (idx % 5) in {shift[0], 3 + shift[0]}:
                if pi_right is not None:
                    if type(pi_right) == str:
                        print('string error occoured!')
                        print(crawler_list[-1].as_dict())
                    config = Config(name='CONFIGURATION_FUNCTIONS/left',
                                    location=location,
                                    pi=-pi_right)
                    pi_right = None
                else:
                    config = Config(name='CONFIGURATION_FUNCTIONS/left',
                                    location=location)
                    pi_left = config.pi
                flag = 'left'

            elif (idx % 5) in {shift[1], 3 + shift[1]}:
                if pi_left is not None:
                    if type(pi_left) == str:
                        print('string error occoured!')
                        print(crawler_list[-1].as_dict())

                    config = Config(name='CONFIGURATION_FUNCTIONS/right',
                                    location=location,
                                    pi=-pi_left)
                    pi_left = None
                else:
                    config = Config(name='CONFIGURATION_FUNCTIONS/right',
                                    location=location,
                                    )
                    pi_right = config.pi
                flag = 'right'
            else:
                config = Config(name='CONFIGURATION_FUNCTIONS/neutral',
                                location=location, pi=0,
                                media=[],
                                terms=[])
                flag = 'neutral_test'
            proxy = Proxy(name=f'{proxy_type.lower().capitalize()} Proxy',
                          type='HTTP',
                          hostname=single_location.loc[idx]['gateway_ip'],
                          port=int(single_location.loc[idx]['gateway_ip_port']),
                          username=proxy_credentials[proxy_type.upper()][
                              'username'],
                          password=proxy_credentials[proxy_type.upper()][
                              'password'])
            crawler_list.append(
                Crawler(flag=flag, configuration=config, proxy=proxy,
                        experiment_id=exp_id))

    return crawler_list


def launch_experiment(api_token, proxy_credentials):
    exp = Experiment(
        name='Test Experiment testing',
        description='A test of all systems based on a future experiment set up',
        contact='JLadwig',
    )
    # s3_wrapper.fetch_private("/resources/proxies/private_proxies.csv")
    # s3_wrapper.fetch_rotating("/resources/proxies/rotating_proxies.csv")
    s3_wrapper.fetch_geosurf()

    # s3_wrapper.update_valid_cities()

    s3_wrapper.fetch_neutral_domains()
    s3_wrapper.fetch_outlets()

    select_local_outlets(PATH_OUTLETS, PATH_OUTLETS_LOCAL, nr_per_state=2)

    # s3_wrapper.fetch_terms()

    exp_return = api.new_experiment(api_token, exp.as_dict())
    exp_id = Experiment.from_dict(exp_return).id
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

    # Distribute rotating proxies
    # rotating_proxies = pd.read_csv(ROTATING_PATH)
    # rotating_proxies = rotating_proxies.loc[rotating_proxies['active'] == 1]
    # rotating_proxies['gateway_ip_port'] = rotating_proxies[
    #     'gateway_ip_port'].astype(str)
    # location_groups = rotating_proxies.groupby('loc_id')
    # crawler_list += distribute_proxies(location_groups, exp_id, proxy_credentials, "rotating")
    #
    # # Distribute Private Proxies
    # private_proxies = pd.read_csv(PRIVATE_PATH)
    # private_proxies = private_proxies.loc[private_proxies['active'] == 1]
    #
    # private_proxies['gateway_ip_port'] = private_proxies[
    #     'gateway_ip_port'].astype(
    #     str)
    # location_groups = private_proxies.groupby('loc_id')
    # crawler_list += distribute_proxies(location_groups, exp_id, proxy_credentials, "private")

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
    if not os.path.isdir(PRIMEMOVER_PATH + '/resources/crawlers'):
        os.mkdir(PRIMEMOVER_PATH + '/resources/crawlers')
    with open(PRIMEMOVER_PATH + "/resources/crawlers/experiment_3.json",
              'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(access_token=api_token,
                               path=PRIMEMOVER_PATH + "/resources/crawlers/experiment_3.json")
    data_as_dict = json.loads(return_data.text)

    with open(
            f'{PRIMEMOVER_PATH}/resources/crawlers/experiment_3_{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')
    print(exp_id)
    return f"exp_id = {exp_id}"


if __name__ == "__main__":
    with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
        KEYS = json.load(f)

    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    launch_experiment(api_token=key, proxy_credentials=KEYS)
