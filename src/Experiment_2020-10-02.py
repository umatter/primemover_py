from src.worker.Crawler import *
from src.GenerateBenignTerms import GenerateBenignTerms
from src.worker.TimeHandler import Schedule
from datetime import datetime
from src.worker import gdelt_gkg as gkg
import src.worker.api_wrapper as api

PATH_TERMS = "/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv"
PATH_MEDIA_OUTLETS = "/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv"
PATH_INDIVIDUAL_ORG = 'resources/other/individuals.json'
PATH_BENGING_TERMS = 'resources/other/benign_terms.json'

with open("resources/other/testrun_10Oct2020_hometowns.json", 'r') as file:
    LOCATION_LIST = json.load(file)

if __name__ == "__main__":
    gkg.main(50)
    GenerateBenignTerms()

    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=10 * 60 * 60,
                                           end_at=(10 + 23) * 60 * 60)
    Config.MEDIA_DEFAULT_PATH = PATH_MEDIA_OUTLETS
    Config.TERM_DEFAULT_PATH = PATH_TERMS

    # generate neutral crawlers
    config_list_neutral = [
        Config(name='Config/neutral', location=l, pi=0, media={}, terms={}) for
        l in LOCATION_LIST]
    crawler_list_neutral = [Crawler(flag='neutral', configuration=c) for c in
                            config_list_neutral]

    # generate left wing crawlers
    config_list_left = [Config(name='Config/left', location=l) for l in
                        LOCATION_LIST]
    crawler_list_political = [Crawler(flag='left', configuration=c) for c in
                              config_list_left]

    # generate right wing crawlers
    config_list_right = [
        Config(name='Config/right', location=left_config.location,
               pi=- left_config.pi) for left_config in config_list_left]
    crawler_list_political += [Crawler(flag='right', configuration=c) for c in
                               config_list_right]

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

        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': random.choice(benign)})

        individual.add_task(VisitFrequentDirect, to_session=session_id)

        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': neutral})

    for individual in crawler_list_neutral:

        session_id = individual.add_task(VisitFrequentDirect, to_session=True)

        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': random.choice(benign)})

        session_id = individual.add_task(VisitFrequentDirect, to_session=session_id)

        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': neutral})

    crawler_list = crawler_list_neutral + crawler_list_political

    with open("resources/examples/test_crawler_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(path="resources/examples/test_crawler_py.json")
    #
    with open(
            f'resources/crawlers/exp_1_{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(return_data.text, file, indent='  ')
