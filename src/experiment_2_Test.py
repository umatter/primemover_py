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

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

PATH_BENIGN_TERMS = PRIMEMOVER_PATH + '/resources/other/benign_terms.json'

ROTATING_PATH = PRIMEMOVER_PATH + '/resources/proxies/rotating_proxies.csv'

PRIVATE_PATH = PRIMEMOVER_PATH + '/resources/proxies/private_proxies.csv'

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)

if __name__ == "__main__":
    exp = Experiment(
        name='Test Experiment testing',
        description='A test of all systems based on a future experiment set up',
        contact='JLadwig',
    )
    s3_wrapper.fetch_private()
    s3_wrapper.fetch_rotating()
    s3_wrapper.fetch_geosurf()

    s3_wrapper.update_valid_cities()

    s3_wrapper.fetch_outlets()
    s3_wrapper.fetch_terms()

    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    exp_return = api.new_experiment(key, exp.as_dict())
    exp_id = Experiment.from_dict(exp_return).id
    # exp_id = 2
    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=10 * 60 * 60,
                                           end_at=(10 + 23) * 60 * 60,
                                           interval=600,
                                           )
    # Generate GEOSURF based crawlers
    GEO_SURF_PROXIES = 2 * ["US-CO-COLORADO_SPRINGS", "US-CA-SAN_FRANCISCO"]

    # generate neutral configurations
    config_list_neutral = [
        Config(name='Config/neutral', location=l, pi=0, media=[], terms=[]) for
        l in GEO_SURF_PROXIES]
    # generate crawlers from neutral configs
    crawler_list = [
        Crawler(flag='neutral_test', configuration=c, experiment_id=exp_id) for
        c in
        config_list_neutral]
    # generate left and right configs with opposing pi in each location
    config_list_left = [Config(name='Config/left', location=l) for l in
                        GEO_SURF_PROXIES]
    config_list_right = [
        Config(name='Config/right', location=left_config.location,
               pi=left_config.pi) for left_config in
        config_list_left]

    crawler_list += [
        Crawler(flag='left_test', configuration=c, experiment_id=exp_id) for c
        in
        config_list_left]
    crawler_list += [
        Crawler(flag='right_test', configuration=c, experiment_id=exp_id) for c
        in
        config_list_right]

    # Distribute rotating proxies
    rotating_proxies = pd.read_csv(ROTATING_PATH)
    rotating_proxies = rotating_proxies.loc[rotating_proxies['active'] == 1]
    rotating_proxies['gateway_ip_port'] = rotating_proxies[
        'gateway_ip_port'].astype(str)
    location_groups = rotating_proxies.groupby('loc_id')
    for single_location in location_groups:
        pi_left = 'None'
        location = single_location[0]
        single_location = single_location[1].reset_index(drop=True)
        for idx in single_location.index:
            if idx % 3 == 0:
                config = Config(name='Config/left', location=location)
                pi_left = config.pi
                flag = 'left_test'

            elif idx % 3 == 1:
                config = Config(name='Config/right', location=location,
                                pi=-pi_left)
                flag = 'right_test'
            else:
                config = Config(name='Config/neutral', location=location, pi=0,
                                media=[],
                                terms=[])
                flag = 'neutral_test'
            proxy = Proxy(name='Rotating Proxy', type='HTTP',
                          hostname=single_location.loc[idx]['gateway_ip'],
                          port=int(single_location.loc[idx]['gateway_ip_port']),
                          username=KEYS['ROTATING']['username'],
                          password=KEYS['ROTATING']['password'])
            crawler_list.append(
                Crawler(flag=flag, configuration=config, proxy=proxy))

    # Distribute Private Proxies
    private_proxies = pd.read_csv(PRIVATE_PATH)
    private_proxies = private_proxies.loc[private_proxies['active'] == 1]

    private_proxies['gateway_ip_port'] = private_proxies[
        'gateway_ip_port'].astype(
        str)
    location_groups = private_proxies.groupby('loc_id')
    for single_location in location_groups:
        pi_left = 'None'
        location = single_location[0]
        single_location = single_location[1].reset_index(drop=True)
        for idx in single_location.index:
            if idx % 3 == 0:
                config = Config(name='Config/left', location=location)
                pi_left = config.pi
                flag = 'left_test'

            elif idx % 3 == 1:
                config = Config(name='Config/right', location=location,
                                pi=-pi_left)
                flag = 'right_test'
            else:
                config = Config(name='Config/neutral', location=location, pi=0,
                                media=[],
                                terms=[])
                flag = 'neutral_test'
            proxy = Proxy(name='Private Proxy', type='HTTP',
                          hostname=single_location.loc[idx]['gateway_ip'],
                          port=int(single_location.loc[idx]['gateway_ip_port']),
                          username=KEYS['PRIVATE']['username'],
                          password=KEYS['PRIVATE']['password'])
            crawler_list.append(
                Crawler(flag=flag, configuration=config, proxy=proxy))
    with open(PRIMEMOVER_PATH + "/resources/crawlers/test_2.json",
              'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(access_token=key,
                               path=PRIMEMOVER_PATH + "/resources/crawlers/test_2.json")
    data_as_dict = json.loads(return_data.text)

    with open(
            f'{PRIMEMOVER_PATH}/resources/crawlers/test_3_{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')
