"""Assign desired crawlers the task to visit browserleaks.com and all relevant sub sites
J.L. 11.2020
"""
from src.worker.UpdateObject import *
from src.worker.TimeHandler import *
from datetime import datetime, timedelta
import src.worker.api_wrapper as api
from src.base.base_tasks import BrowserLeaks

from src.base.BaseCrawler import BaseCrawler

import json
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())


def single_update(experiment_id, api_credentials,
                  date_time=datetime.now(), crawler_class=BaseCrawler):
    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=12 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)

    api_token = api_wrapper.get_access(api_credentials.get('username'),
                                       api_credentials.get('password'))

    raw_experiment = api_wrapper.fetch_experiment(access_token=api_token, exp_id=
    experiment_id)

    crawler_list = crawler_class.from_list(raw_experiment['crawlers'],
                                           date_time=date_time)
    # crawler_list = UpdateObject(crawler_list, 'config')
    with open(PRIMEMOVER_PATH + '/resources/other/to_process.json',
              'r') as file:
        ids_to_process = json.load(file)

    crawler_list_2 = []
    for individual in crawler_list:
        if individual.crawler_info.crawler_id in ids_to_process:
            individual.add_task(BrowserLeaks)
            crawler_list_2.append(individual)
    crawler_list = crawler_list_2
    # [c.add_task(BrowserLeaks) for c in crawler_list]

    queues = [c.queues[0] for c in crawler_list]
    t_0 = datetime.fromisoformat(
        f'{date_time.date().isoformat()}T12:00:00')
    print(t_0)
    delta_t_1 = int(90)

    for q in queues[0:]:
        q.start_at = t_0.isoformat()
        t_0 += timedelta(seconds=delta_t_1)
    with open(PRIMEMOVER_PATH + "/resources/updates/generated.json",
              'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(access_token=api_token,
                               path=PRIMEMOVER_PATH + "/resources/updates/generated.json")
    data_as_dict = json.loads(return_data.text)
    with open(
            f'{PRIMEMOVER_PATH}/resources/updates/exp_3_{(date_time.date()).isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')


if __name__ == "__main__":
    PRIMEMOVER_PATH = str(
        pathlib.Path(__file__).parent.parent.parent.absolute())

    with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
        KEYS = json.load(f)
    single_update(experiment_id=46, date_time=datetime.now(), api_credentials=KEYS.get("PRIMEMOVER"))
