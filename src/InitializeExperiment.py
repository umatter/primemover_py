from src.ConfigureProfile import *
from src.Tasks import *
import itertools
import json
from src.TimeHandler import Schedule
from src.Crawler import *

PATH_TERMS = "/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv"
PATH_MEDIA_OUTLETS = "/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv"

if __name__ == "__main__":
    global_schedule = Schedule(start_at=8 * 60 * 60, end_at=(8 + 23) * 60 * 60)

    nr_ind = int(input("Please input the desired nr. of individuals: "))
    Config.MEDIA_DEFAULT_PATH = PATH_MEDIA_OUTLETS
    Config.TERM_DEFAULT_PATH = PATH_TERMS
    crawler_list = [Crawler(global_schedule=global_schedule, proxies=Proxy()) for i in
                    range(nr_ind)]
    for individual in crawler_list:
        individual.add_searches(10)
        individual.add_direct_visits(10)

    with open("resources/examples/example_crawler_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')
