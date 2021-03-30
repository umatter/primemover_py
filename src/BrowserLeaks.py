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

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)



def single_update(day_delta=0):
    existing_crawler_path = PRIMEMOVER_PATH + "/resources/crawlers/test_3_2021-01-22.json"
    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)

    with open(existing_crawler_path, 'r') as file:
        raw_crawlers = json.load(file)
    crawler_list = Crawler.from_dict(raw_crawlers, day_delta=day_delta)

    for individual in crawler_list:
        individual.add_task(BrowserLeaks)
    with open(PRIMEMOVER_PATH + "/resources/examples/test_update_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
              indent='  ')
    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    return_data = api.push_new(access_token=key, path=PRIMEMOVER_PATH + "/resources/examples/test_update_py.json")
    data_as_dict = json.loads(return_data.text)
    with open(
            f'{PRIMEMOVER_PATH}/resources/updates/exp_2_{(datetime.now().date() + timedelta(days=day_delta)).isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')


if __name__ == "__main__":
    single_update(day_delta=0)
