from src.worker import Crawler, Tasks, ConfigureProfile
from src.auxiliary.GenerateBenignTerms import GenerateBenignTerms
from src.worker.TimeHandler import Schedule, TimeHandler
from datetime import datetime, timedelta
import src.worker.api_wrapper as api
import random as r
import json
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

PATH_BENIGN_TERMS = PRIMEMOVER_PATH + '/resources/other/benign_terms.json'

NEUTRAL_1 = ["White House", "Congress", "Mail-in ballot", "Polling station",
             "Joe Biden", "Donald Trump", "Democrat", "Republican"]

NEUTRAL_2 = ["Joe Biden", "Donald Trump", "Nevada", "Pennsylvania", "Georgia",
             "Arizona", "Wisconsin", "Michigan", "count votes", "stop count",
             "illegal ballots", "electoral vote", "voter fraud"]

NEUTRAL_3 = ["Georgia", "senate race", "recount", "presidential transition",
             "president-elect", "electoral vote", "voter fraud",
             "did my vote count?", "google news"]
NEUTRAL_4 = ["Georgia recount",
             "Donald Trump is",
             "Joe Biden is",
             "senate race",
             "presidential transition",
             "electoral vote",
             "mask mandate",
             "curfew",
             "jobless claims",
             "Michigan election",
             "voter fraud",
             "did my vote count?",
             "google news"]

NEUTRAL = ["Sidney Powell", "Donald Trump is", "Joe Biden is", "covid vaccine",
           "presidential transition", "mask mandate", "curfew",
           "has michigan certified the election",
           "has pennsylvania certified the election", "voter fraud",
           "election results 2020", "news"]


def single_update(day_delta=0):
    GenerateBenignTerms()

    # existing_crawler_path = f'{PRIMEMOVER_PATH}/resources/updates/exp_2_{(datetime.now().date()+ timedelta(days=-1)).isoformat()}.json'
    existing_crawler_path = PRIMEMOVER_PATH + "/resources/crawlers/2020-10-23.json"
    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)

    with open(existing_crawler_path, 'r') as file:
        raw_crawlers = json.load(file)
    crawler_list_combined = Crawler.Crawler.from_list(raw_crawlers,
                                                      day_delta=day_delta)
    crawler_list_neutral = []
    crawler_list_political = []
    for crawler in crawler_list_combined:
        if crawler.flag in {'right', 'left'}:
            crawler_list_political.append(crawler)
        else:
            crawler_list_neutral.append(crawler)

    neutral = r.choices(NEUTRAL, k=2)
    with open(PATH_BENIGN_TERMS, 'r') as file:
        benign = json.load(file)

    for individual in crawler_list_political:

        session_id = individual.add_task(Tasks.BenignGoogleSearch,
                                         to_session=True,
                                         params={'term': r.choice(benign)})
        if r.choice([True, False]):
            individual.add_task(Tasks.PoliticalSearchNoUtility,
                                to_session=True,
                                params={'term_type': 'bigrams'})
        if r.choice([True, False]):
            individual.add_task(Tasks.PoliticalSearchNoUtility,
                                to_session=session_id,
                                params={'term_type': 'instagram'})
        if r.choice([True, False]):
            individual.add_task(Tasks.VisitMediaGoogleNoUtility,
                                to_session=session_id)
        if r.choice([True, False]):
            individual.add_task(Tasks.VisitMediaNoUtility,
                                to_session=session_id)
        if r.choice([True, False]):
            individual.add_task(Tasks.VisitFrequentDirect,
                                to_session=session_id)

        individual.add_task(Tasks.NeutralGoogleSearch, to_session=True,
                            params={'term': neutral[0]})
        individual.add_task(Tasks.NeutralGoogleSearch, to_session=True,
                            params={'term': neutral[1]})

    for individual in crawler_list_neutral:
        session_id = individual.add_task(Tasks.BenignGoogleSearch,
                                         to_session=True,
                                         params={'term': r.choice(benign)})
        if r.choice([True, False]):
            individual.add_task(Tasks.VisitFrequentDirect,
                                to_session=session_id)

        individual.add_task(Tasks.NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[0]})
        individual.add_task(Tasks.NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[1]})

    crawler_list = crawler_list_neutral + crawler_list_political

    with open(PRIMEMOVER_PATH + "/resources/examples/test_update_py.json",
              'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    do = input('push data? (y/n): ')
    if do == 'y':
        return_data = api.push_new(
            path=PRIMEMOVER_PATH + "/resources/examples/test_update_py.json")
        data_as_dict = json.loads(return_data.text)
        with open(
                f'{PRIMEMOVER_PATH}/resources/updates/exp_2_{(datetime.now().date() + timedelta(days=day_delta)).isoformat()}.json',
                'w') as file:
            json.dump(data_as_dict, file, indent='  ')


if __name__ == "__main__":
    # for day in range(13):
    #     single_update(day_delta=day)
    #     print((datetime.now().date() + timedelta(days=day)).isoformat())
    single_update(day_delta=0)
