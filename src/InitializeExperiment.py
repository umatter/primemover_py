import requests
import json
from src.TimeHandler import Schedule
from src.Crawler import *
import src.gdelt_gkg as gkg
import src.api_wrapper as api
from src.GenerateBenignTerms import GenerateBenignTerms

PATH_TERMS = "/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv"
PATH_MEDIA_OUTLETS = "/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv"
PATH_INDIVIDUAL_ORG = 'resources/other/individuals.json'
PATH_BENGING_TERMS = 'resources/other/benign_terms.json'
# gkg.main(50)
GenerateBenignTerms()

if __name__ == "__main__":
    global_schedule = Schedule(start_at=8 * 60 * 60, end_at=(8 + 23) * 60 * 60)
    nr_ind = int(input("Please input the desired nr. of individuals: "))
    Config.MEDIA_DEFAULT_PATH = PATH_MEDIA_OUTLETS
    Config.TERM_DEFAULT_PATH = PATH_TERMS
    crawler_list = [
        Crawler(global_schedule=global_schedule, name=f'test_crawler_{i}')
        for i in
        range(nr_ind)]
    with open(PATH_INDIVIDUAL_ORG, 'r') as file:
        neutral = json.load(file)[0]
    with open(PATH_INDIVIDUAL_ORG, 'r') as file:
        benign = json.load(file)

    for individual in crawler_list:
        session_id = individual.add_searches(nr=2, to_session=True)
        individual.add_direct_visits(nr=2, to_session=session_id)

        site_to_visit = random.choice(
            ['https://www.amazon.com', 'https://www.ebay.com'])

        individual.add_direct_visits(outlets=site_to_visit,
                                     to_session=session_id)
        individual.add_direct_visits(outlets=site_to_visit,
                                     to_session=session_id)
        individual.add_searches(terms=random.choice(benign),
                                to_session=session_id)
        individual.add_searches(terms=neutral,
                                to_session=session_id)

    with open("resources/examples/test_crawler_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    # return_data = api.push_new(path="resources/examples/test_crawler_py.json")
    #
    # with open("resources/examples/return_data_api.json", 'w') as file:
    #     json.dump(return_data.text, file, indent='  ')
