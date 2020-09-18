import requests
import json
from src.TimeHandler import Schedule
from src.Crawler import *
import src.gdelt_gkg as gkg
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
    crawler_list = [Crawler(global_schedule=global_schedule, proxies=Proxy())
                    for i in
                    range(nr_ind)]
    with open(PATH_INDIVIDUAL_ORG, 'r') as file:
        neutral = json.load(file)[0]
    with open(PATH_INDIVIDUAL_ORG, 'r') as file:
        benign = json.load(file)

    for individual in crawler_list:
        times = individual.schedule.consecutive_times(7)
        individual.add_searches(2, times[0:2])
        individual.add_direct_visits(2, times[2:4])
        site_to_visit = random.choice(
            ['https://www.amazon.com', 'https://www.ebay.com'])
        individual.queues.append(VisitDirect(site_to_visit, times[4]))
        individual.queues.append(GoogleSearch(random.choice(benign), times[5]))
        individual.queues.append(GoogleSearch(neutral, times[6]))

    with open("resources/examples/example_crawler_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

