from src.worker import Crawler, Tasks, ConfigureProfile, s3_wrapper, Experiment
from src.worker.UpdateObject import *
from src.worker.ReplaceProxies import update_all_proxies
from src.auxiliary.GenerateBenignTerms import GenerateBenignTerms
from src.worker.TimeHandler import Schedule, TimeHandler
from datetime import datetime, timedelta
import src.worker.api_wrapper as api
import random as r
import json
import pathlib
import os

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

PATH_BENIGN_TERMS = PRIMEMOVER_PATH + '/resources/other/benign_terms.json'

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)


def single_update(date, default_crawler_path, manual=False):
    "Fetch Neutral terms from s3 Bucket"
    neutral_path = PRIMEMOVER_PATH + '/resources/input_data/neutral_searchterms_pool.json'
    if not os.path.exists(neutral_path):
        Neutral = s3_wrapper.fetch_neutral()
    else:
        with open(neutral_path) as file:
            Neutral = json.load(file)
    if len(Neutral) == 0:
        Neutral = s3_wrapper.fetch_neutral()
    neutral = Neutral[0:3]

    "Generate Benign Terms TODO: "
    GenerateBenignTerms()

    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)
    if not os.path.exists(
            f'{PRIMEMOVER_PATH}/resources/updates/{(date + timedelta(-1)).isoformat()}.json'):
        existing_crawler_path = PRIMEMOVER_PATH + default_crawler_path
    else:
        existing_crawler_path = f'{PRIMEMOVER_PATH}/resources/updates/{(date + timedelta(-1)).isoformat()}.json'

    with open(existing_crawler_path, 'r') as file:
        raw_crawlers = json.load(file)

    crawler_list = Crawler.Crawler.from_dict(raw_crawlers, date=date)
    crawler_list = UpdateObject(crawler_list, 'agent')
    crawler_list = UpdateObject(crawler_list, 'proxy')
    crawler_list = UpdateObject(crawler_list, 'config')

    "Compute Proxy Changes"
    update_proxies_dict = update_all_proxies()

    crawler_list_neutral = []
    crawler_list_political = []
    for crawler in crawler_list:
        if crawler.flag in {'right_test', 'left_test'}:
            crawler_list_political.append(crawler)
        else:
            crawler_list_neutral.append(crawler)

    if os.path.exists(
            f'{PRIMEMOVER_PATH}/resources/cleaned_data/{date.isoformat()}.json'):
        with open(
                f'{PRIMEMOVER_PATH}/resources/cleaned_data/{date.isoformat()}.json',
                'r') as file:
            cleaned_data = json.load(file)
        crawler_list_neutral = [
            crawler.update_crawler(proxy_update=update_proxies_dict) for crawler
            in crawler_list_neutral]
        crawler_list_political = [
            crawler.update_crawler(results=cleaned_data,
                                   proxy_update=update_proxies_dict) for crawler
            in crawler_list_political]

    with open(PATH_BENIGN_TERMS, 'r') as file:
        benign = json.load(file)

    for individual in crawler_list_political:
        session_id = individual.add_task(Tasks.BenignGoogleSearch,
                                         to_session=True,
                                         params={'term': r.choice(benign)})
        individual.add_task(Tasks.PoliticalSearch,
                            to_session=session_id)

        individual.add_task(Tasks.VisitMedia,
                            to_session=session_id)
        individual.add_task(Tasks.VisitFrequentDirect,
                            to_session=session_id)

        individual.add_task(Tasks.PoliticalSearch,
                            to_session=session_id, )

        individual.add_task(Tasks.VisitMedia,
                            to_session=session_id)
        individual.add_task(Tasks.VisitFrequentDirect,
                            to_session=session_id)

        individual.add_task(Tasks.NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[0]})

    for individual in crawler_list_neutral:
        session_id = individual.add_task(Tasks.BenignGoogleSearch,
                                         to_session=True,
                                         params={'term': r.choice(benign)})

        individual.add_tasks(Tasks.VisitFrequentDirect, nr=2,
                             to_session=session_id)

        individual.add_task(Tasks.NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[0]})

    crawler_list = crawler_list_neutral + crawler_list_political

    with open(PRIMEMOVER_PATH + "/resources/updates/generated.json",
              'w') as file:
        json.dump(
            [crawler.as_dict(object_ids=False) for crawler in crawler_list],
            file,
            indent='  ')
    # Create complete copy of crawlers
    for c in crawler_list:
        c.send_agent = True

    with open(PRIMEMOVER_PATH + "/resources/updates/complete.json",
              'w') as file:
        json.dump(
            [crawler.as_dict(object_ids=True) for crawler in crawler_list],
            file,
            indent='  ')

    if manual:
        do = input('push data? (y/n): ')
    else:
        do = 'y'
    if do == 'y':
        key = api.get_access(KEYS['PRIMEMOVER']['username'],
                             KEYS['PRIMEMOVER']['password'])

        return_data = api.push_new(access_token=key,
                                   path=f'{PRIMEMOVER_PATH}/resources/updates/generated.json')
        if return_data.status_code == 200:
            with open(
                    f'{PRIMEMOVER_PATH}/resources/updates/{date.date().isoformat()}.json',
                    'w') as file:
                json.dump(return_data.json(), file, indent='  ')
            # Delete neutral terms if push was successful
            with open(neutral_path, 'w') as file:
                json.dump(Neutral[3:], file)
        else:
            print(return_data)

        # experiment = api.update_experiment(key, [exp.as_dict()], exp.id)
        # print(experiment)


if __name__ == "__main__":
    # for day in range(13):
    #     single_update(day_delta=day)
    #     print((datetime.now().date() + timedelta(days=day)).isoformat())
    single_update(datetime.now(),
                  default_crawler_path="/resources/crawlers/test_6_2021-06-01.json",
                  manual=True)
