"""Assign desired crawlers the task to visit browserleaks.com and all relevant sub sites
J.L. 11.2020
"""
from src.worker.UpdateObject import *
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



def single_update(experiment_id, date = datetime.now()):
    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)

    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    raw_experiment = api_wrapper.fetch_experiment(access_token=key, id=
    experiment_id)

    crawler_list = Crawler.from_list(raw_experiment['crawlers'],
                                             date=date)
    temp_list = []
    for c in crawler_list:
        if c.crawler_info.crawler_id in [994, 1012, 1032, 1040, 1086, 1089, 1163, 1167, 1190, 1191, 1194, 1198, 1199, 1202, 1208, 1213, 1215, 1218, 1219, 1226]:
            temp_list.append(c)
    crawler_list = temp_list
    for individual in crawler_list:
        individual.schedule = TimeHandler("US-NY-NEW_YORK",
                                     interval=120,
                                     wake_time=9 * 60 * 60,
                                     bed_time=10 * 60 * 60,
                                     date=date)
        individual.add_task(BrowserLeaks)
    with open(PRIMEMOVER_PATH + "/resources/updates/generated.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
              indent='  ')
    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    return_data = api.push_new(access_token=key, path=PRIMEMOVER_PATH + "/resources/updates/generated.json")
    data_as_dict = json.loads(return_data.text)
    with open(
            f'{PRIMEMOVER_PATH}/resources/updates/exp_2_{(date.date()).isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')


if __name__ == "__main__":
    single_update(experiment_id=36, date=datetime.now())
