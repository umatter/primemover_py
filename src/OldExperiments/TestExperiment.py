from src.worker.Crawler import *
from src.auxiliary.GenerateBenignTerms import GenerateBenignTerms
from src.worker.TimeHandler import Schedule
from datetime import datetime
import src.worker.api_wrapper as api

PATH_TERMS = "/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv"
PATH_MEDIA_OUTLETS = "/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv"
PATH_INDIVIDUAL_ORG = 'resources/other/individuals.json'
PATH_BENGING_TERMS = 'resources/other/benign_terms.json'
# gkg.main(50)
GenerateBenignTerms()

if __name__ == "__main__":

    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=8 * 60 * 60,
                                           end_at=(8 + 23) * 60 * 60)
    nr_ind = int(input("Please input the desired nr. of individuals: "))
    Config.MEDIA_DEFAULT_PATH = PATH_MEDIA_OUTLETS
    Config.TERM_DEFAULT_PATH = PATH_TERMS
    crawler_list = [
        Crawler(name=f'test_crawler_{i}')
        for i in
        range(nr_ind)]
    with open(PATH_INDIVIDUAL_ORG, 'r') as file:
        neutral = json.load(file)[0]
    with open(PATH_INDIVIDUAL_ORG, 'r') as file:
        benign = json.load(file)

    for individual in crawler_list:
        # Add political searches from bots search term library
        session_id = individual.add_tasks(PoliticalSearch, nr=2,
                                          to_session=True)
        # Add direct
        individual.add_tasks(VisitMedia, nr=2, to_session=session_id)

        site_to_visit = random.choice(
            ['https://www.amazon.com', 'https://www.ebay.com'])
        individual.add_task(VisitDirect, to_session=session_id,
                            params={'outlet_url': site_to_visit})
        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': random.choice(benign)})
        individual.add_task(GoogleSearch, to_session=session_id,
                            params={'term': neutral})

    with open("resources/examples/test_crawler_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(path="resources/examples/test_crawler_py.json")
    #
    with open(f'resources/crawlers/existing_{datetime.now().date().isoformat()}.json', 'w') as file:
        json.dump(return_data.text, file, indent='  ')
