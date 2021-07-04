"""
Experiment partisan google elections 2020-10-21
This file generates new crawlers, in particular the required config files

J.L. 11.2020
"""

from src.worker.Crawler import Crawler
from src.worker.TimeHandler import Schedule, TimeHandler
from src.worker.ConfigureProfile import Config
from src.worker import api_wrapper as api
from src.worker import s3_wrapper
import json
import pandas as pd
from src.worker.Experiment import Experiment
from datetime import datetime
import pathlib
from src.worker.Proxy import Proxy
import random as r

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

PATH_BENIGN_TERMS = PRIMEMOVER_PATH + '/resources/other/benign_terms.json'

ROTATING_PATH = PRIMEMOVER_PATH + '/resources/proxies/rotating_proxies.csv'

PRIVATE_PATH = PRIMEMOVER_PATH + '/resources/proxies/private_proxies.csv'

GEOSURF_PATH = PRIMEMOVER_PATH + '/resources/proxies/geosurf_proxies.csv'
with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)


def distribute_proxies(location_groups,exp_id, proxy_type="rotating"):
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
                    config = Config(name='Config/left', location=location,
                                    pi=-pi_right)
                    pi_right = None
                else:
                    config = Config(name='Config/left', location=location)
                    pi_left = config.pi
                flag = 'left'

            elif (idx % 5) in {shift[1], 3 + shift[1]}:
                if pi_left is not None:
                    if type(pi_left) == str:
                        print('string error occoured!')
                        print(crawler_list[-1].as_dict())

                    config = Config(name='Config/right', location=location,
                                    pi=-pi_left)
                    pi_left = None
                else:
                    config = Config(name='Config/right', location=location,
                                    )
                    pi_right = config.pi
                flag = 'right'
            else:
                config = Config(name='Config/neutral', location=location, pi=0,
                                media=[],
                                terms=[])
                flag = 'neutral_test'
            proxy = Proxy(name=f'{proxy_type.lower().capitalize()} Proxy', type='HTTP',
                          hostname=single_location.loc[idx]['gateway_ip'],
                          port=int(single_location.loc[idx]['gateway_ip_port']),
                          username=KEYS[proxy_type.upper()]['username'],
                          password=KEYS[proxy_type.upper()]['password'])
            crawler_list.append(
                Crawler(flag=flag, configuration=config, proxy=proxy,
                        experiment_id=exp_id))

    return crawler_list


def launch_experiment():
    exp = Experiment(
        name='Test Experiment testing',
        description='A test of all systems based on a future experiment set up',
        contact='JLadwig',
    )
    s3_wrapper.fetch_private("/resources/proxies/private_proxies.csv")
    s3_wrapper.fetch_rotating("/resources/proxies/rotating_proxies.csv")
    s3_wrapper.fetch_geosurf()

    s3_wrapper.update_valid_cities()

    s3_wrapper.fetch_neutral_domains()
    s3_wrapper.fetch_outlets()
    s3_wrapper.fetch_terms()

    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    exp_return = api.new_experiment(key, exp.as_dict())
    exp_id = Experiment.from_dict(exp_return).id

    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=10 * 60 * 60,
                                           end_at=(10 + 23) * 60 * 60,
                                           interval=600,
                                           )
    # Generate GEOSURF based crawlers
    GEO_SURF_PROXIES = ["US-CO-COLORADO_SPRINGS",
                            "US-OK-OKLAHOMA_CITY",
                            "US-KS-WICHITA",
                            "US-CA-BAKERSFIELD",
                            "US-FL-JACKSONVILLE",
                            "US-CA-SAN_FRANCISCO",
                            "US-WI-MADISON",
                            "US-CA-SAN_JOSE",
                            "US-DC-WASHINGTON",
                            "US-TX-EL_PASO"]

    # generate neutral configurations
    config_list_neutral = [
        Config(name='Config/neutral', location=l, pi=0, media=[], terms=[]) for
        l in 2 * GEO_SURF_PROXIES]
    # generate crawlers from neutral configs
    crawler_list = [
        Crawler(flag='neutral_test', configuration=c, experiment_id=exp_id) for
        c in
        config_list_neutral]
    # generate left and right configs with opposing pi in each location
    config_list_left = [Config(name='Config/left', location=l) for l in
                        4 * GEO_SURF_PROXIES]
    config_list_right = [
        Config(name='Config/right', location=left_config.location,
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
    rotating_proxies = pd.read_csv(ROTATING_PATH)
    rotating_proxies = rotating_proxies.loc[rotating_proxies['active'] == 1]
    rotating_proxies['gateway_ip_port'] = rotating_proxies[
        'gateway_ip_port'].astype(str)
    location_groups = rotating_proxies.groupby('loc_id')
    crawler_list += distribute_proxies(location_groups,exp_id, "rotating" )

    # Distribute Private Proxies
    private_proxies = pd.read_csv(PRIVATE_PATH)
    private_proxies = private_proxies.loc[private_proxies['active'] == 1]

    private_proxies['gateway_ip_port'] = private_proxies[
        'gateway_ip_port'].astype(
        str)
    location_groups = private_proxies.groupby('loc_id')
    crawler_list += distribute_proxies(location_groups, exp_id, "private")

    with open(PRIMEMOVER_PATH + "/resources/crawlers/experiment_2.json",
              'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(access_token=key,
                               path=PRIMEMOVER_PATH + "/resources/crawlers/experiment_2.json")
    data_as_dict = json.loads(return_data.text)

    with open(
            f'{PRIMEMOVER_PATH}/resources/crawlers/experiment_2{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')

    return f"exp_id = {exp_id}"


if __name__ == "__main__":
    launch_experiment()
