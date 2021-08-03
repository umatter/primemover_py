"""
Experiment partisan google elections 2020-10-21
This file generates new crawlers, in particular the required config files

J.L. 11.2020
"""
from src.worker.Crawler import Crawler
from src.worker.TimeHandler import Schedule, TimeHandler
from src.worker import api_wrapper as api
from src.worker import s3_wrapper
import json
from src.worker.Experiment import Experiment
from datetime import datetime
import pathlib
from src.worker.Proxy import Proxy
from src.worker.Agent import Agent
from src.worker import Tasks


PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)


def launch_test():
    exp = Experiment(
        name='Test Experiment testing',
        description='A test of all systems',
        contact='JLadwig',
    )

    s3_wrapper.update_valid_cities()

    s3_wrapper.fetch_outlets()
    s3_wrapper.fetch_terms()

    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    # exp_return = api.new_experiment(key, exp.as_dict())
    # exp_id = Experiment.from_dict(exp_return).id
    exp_id = 29
    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=10 * 60 * 60,
                                           end_at=(10 + 23) * 60 * 60,
                                           interval=600,
                                           )

    # generate neutral configurations

    # generate crawlers from neutral configs

    crawler_list = [
        Crawler(flag='stress_test',
                experiment_id=exp_id,
                agent=Agent(location='US-NY-NEW_YORK')
                ) for i in range(0, 350)]

    for c in crawler_list:
        c.send_agent = True
        session_id = c.add_task(Tasks.VisitFrequentDirect)
        c.add_task(Tasks.VisitFrequentDirect, to_session=session_id)
        c.add_task(Tasks.VisitFrequentDirect, to_session=session_id)
    crawler_dict = []
    for c in crawler_list:
        c_dict = c.as_dict()
        c_dict.pop('proxy')
        crawler_dict.append(c_dict)
    with open(PRIMEMOVER_PATH + "/resources/crawlers/stress_test.json",
              'w') as file:
        json.dump(crawler_dict, file,
                  indent='  ')

    return_data = api.push_new(access_token=key,
                               path=PRIMEMOVER_PATH + "/resources/crawlers/stress_test.json")
    data_as_dict = json.loads(return_data.text)

    with open(
            f'{PRIMEMOVER_PATH}/resources/crawlers/stress_test_{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')

    return f"exp_id = {exp_id}"


if __name__ == "__main__":
    launch_test()
