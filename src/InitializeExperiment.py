from src.ConfigureProfile import *
from src.Tasks import *
import itertools
import json
from src.Crawler import *
PATH_TERMS = "/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv"
PATH_MEDIA_OUTLETS="/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv"

if __name__ == "__main__":
    nr_ind = int(input("Please input the desired nr. of individuals: "))
    crawler_config = [Config(path_terms=PATH_TERMS, path_media_outlets=PATH_MEDIA_OUTLETS) for i in range(0, nr_ind)]
    config_data ="\n,".join([single.__str__() for single in crawler_config])
    with open("resources/examples/example_config.json", 'w') as file:
        file.write(f'{{"configurations":[{config_data}]}}')

    crawler_list = [Crawler(crawler_info=config.config_info.new_crawler()) for config in crawler_config]
    for individual in crawler_list:
        individual.queues.append(GoogleSearch('insert term here', 'insert time here', individual.crawler_info.new_queue()))
        individual.queues.append(VisitDirect('https://www.nytimes.com', 'insert time here', individual.crawler_info.new_queue()))

    crawler_data = "\n,".join([single.__str__() for single in crawler_list])
    with open("resources/examples/example_crawler.json", 'w') as file:
        file.write(f'{{"data":[{crawler_data}]}}')

