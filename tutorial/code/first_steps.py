from src.base.BaseCrawler import BaseCrawler
from src.base.BaseConfig import BaseConfig
from src.base import base_tasks as tasks
from src.base import Results

from src.worker import s3_wrapper
from src.worker.TimeHandler import TimeHandler, Schedule
from src.worker import api_wrapper as api
from datetime import datetime, timedelta
from src.worker.Experiment import Experiment

import json
import pathlib

PRIMEMOVER_PATH = str(
    pathlib.Path(__file__).parent.parent.parent.absolute())


def first_crawler(api_token, update_valid_cities=False, push=True):
    """
    wrapped version of the code found in 1 first steps.md.,
    Param:
        update_valid_cities, Bool: If False, first_crawler will not attempt to fetch valid_cities from s3
        push, Bool: if False, no new experiment will be created and no queues will be pushed
    """
    if update_valid_cities:
        s3_wrapper.update_valid_cities()

    exp = Experiment(
        name='Test Experiment',
        description='A first step towards using primemover_py',
        contact='you',
    )
    if push:
        exp_return = api.new_experiment(api_token, exp.as_dict())
        exp_id = Experiment.from_dict(exp_return).id
    else:
        exp_id = 0

    first_config = BaseConfig(location='US-AZ-PHOENIX')

    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)

    schedule = TimeHandler('US-AZ-PHOENIX',
                           interval=120,
                           wake_time=10 * 60 * 60,
                           bed_time=17 * 60 * 60
                           )

    second_crawler = BaseCrawler(configuration=first_config, schedule=schedule, experiment_id=exp_id)

    second_crawler.add_task(tasks.BrowserLeaks)
    t_0 = datetime.now() + timedelta(minutes=1)
    second_crawler.queues[0].start_at = t_0

    with open(
            PRIMEMOVER_PATH + "/resources/crawlers/experiment_first_steps.json",
            'w') as file:
        json.dump([second_crawler.as_dict()], file,
                  indent='  ')
    if push:
        return_data = api.push_new(access_token=api_token,
                                   path=PRIMEMOVER_PATH + "/resources/crawlers/experiment_first_steps.json")
        data_as_dict = json.loads(return_data.text)
        with open(
                f'{PRIMEMOVER_PATH}/resources/crawlers/experiment_first_steps_{datetime.now().date().isoformat()}.json',
                'w') as file:
            json.dump(data_as_dict, file, indent='  ')

    return exp_id


if __name__ == "__main__":

    with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
        KEYS = json.load(f)
    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    first_crawler(key, False, False)
