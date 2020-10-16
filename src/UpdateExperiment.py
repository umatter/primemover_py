from src.worker.Crawler import *
from src.GenerateBenignTerms import GenerateBenignTerms
from src.worker.TimeHandler import Schedule
from datetime import datetime, timedelta
from src.worker import gdelt_gkg as gkg
import src.worker.api_wrapper as api

PATH_TERMS = "/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv"
PATH_MEDIA_OUTLETS = "/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv"
PATH_INDIVIDUAL_ORG = 'resources/other/individuals.json'
PATH_BENGING_TERMS = 'resources/other/benign_terms.json'

if __name__ == "__main__":
    gkg.main(50)
    GenerateBenignTerms()

    existing_crawler_path = f'resources/updates/{(datetime.now().date() + timedelta(days=-1)).isoformat()}.json'
    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=8 * 60 * 60,
                                           end_at=(8 + 23) * 60 * 60)

    Config.MEDIA_DEFAULT_PATH = PATH_MEDIA_OUTLETS
    Config.TERM_DEFAULT_PATH = PATH_TERMS

    with open(existing_crawler_path, 'r') as file:
        raw_crawlers = json.load(file)
    crawler_list_combined = Crawler.from_dict(raw_crawlers)
    crawler_list_neutral = []
    crawler_list_political = []
    for crawler in crawler_list_combined:
        if crawler.flag in {'right', 'left'}:
            crawler_list_political.append(crawler)
        else:
            crawler_list_neutral.append(crawler)

    with open(PATH_INDIVIDUAL_ORG, 'r') as file:
        neutral = json.load(file)[0]
    with open(PATH_INDIVIDUAL_ORG, 'r') as file:
        benign = json.load(file)

    for individual in crawler_list_political:
        # Add political search from bots search term library
        session_id = individual.add_task(PoliticalSearch, to_session=True)
        # Add direct
        individual.add_task(VisitMedia, to_session=session_id)

        individual.add_task(PoliticalSearch, to_session=session_id)

        individual.add_task(VisitFrequentDirect, to_session=session_id)

        individual.add_task(PoliticalSearch, to_session=session_id)

        individual.add_task(VisitMedia, to_session=session_id)

        individual.add_task(GoogleSearch,
                            to_session=session_id,
                            params={'term': random.choice(benign),
                                    'search_type': 'benign'})

        individual.add_task(VisitFrequentDirect, to_session=session_id)

        individual.add_task(VisitMedia, to_session=session_id)

        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': neutral,
                                    'search_type': 'neutral'})

    for individual in crawler_list_neutral:
        session_id = individual.add_task(VisitFrequentDirect, to_session=True)

        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': random.choice(benign),
                                    'search_type': 'neutral'})

        session_id = individual.add_task(VisitFrequentDirect,
                                         to_session=session_id)

        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': neutral,
                                    'search_type': 'neutral'})

    crawler_list = crawler_list_neutral + crawler_list_political

    with open("resources/examples/test_update_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(path="resources/examples/test_update_py.json")
    data_as_dict = json.loads(return_data.text)
    with open(f'resources/updates/{datetime.now().date().isoformat()}.json',
              'w') as file:
        json.dump(data_as_dict, file, indent='  ')
