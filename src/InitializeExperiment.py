from src.ConfigureProfile import *
from src.Tasks import *
import itertools
import json
from src.Crawler import *
PATH_TERMS = "/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv"
PATH_MEDIA_OUTLETS="/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv"

if __name__ == "__main__":
    nr_ind = int(input("Please input the desired nr. of individuals: "))
    Config.MEDIA_DEFAULT_PATH = PATH_MEDIA_OUTLETS
    Config.TERM_DEFAULT_PATH = PATH_TERMS
    crawler_list = [Crawler(agents=Agent(), proxies=Proxy()) for i in range(nr_ind)]
    for individual in crawler_list:
        individual.queues.append(GoogleSearch('insert term here', 'insert time here'))
        individual.queues.append(VisitDirect('https://www.nytimes.com', 'insert time here'))

    with open("resources/examples/example_crawler_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file, indent='  ')
