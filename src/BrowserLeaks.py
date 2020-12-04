"""Assign desired crawlers the task to visit browserleaks.com and all relevant sub sites
J.L. 11.2020
"""

from src.worker.Crawler import *
from src.worker.TimeHandler import Schedule
from datetime import datetime, timedelta
import src.worker.api_wrapper as api
from src.worker.Tasks import BrowserLeaks
import json
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())


def single_update(day_delta=0):
    existing_crawler_path = PRIMEMOVER_PATH + "/resources/crawlers/2020-10-23.json"
    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)

    with open(existing_crawler_path, 'r') as file:
        raw_crawlers = json.load(file)
    crawler_list = Crawler.from_list(raw_crawlers, day_delta=day_delta)

    for individual in crawler_list:
        individual.add_task(BrowserLeaks)

        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(path=PRIMEMOVER_PATH + "/resources/examples/test_update_py.json")
    data_as_dict = json.loads(return_data.text)
    with open(
            f'{PRIMEMOVER_PATH}/resources/updates/exp_2_{(datetime.now().date() + timedelta(days=day_delta)).isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')


if __name__ == "__main__":
    single_update(day_delta=0)
