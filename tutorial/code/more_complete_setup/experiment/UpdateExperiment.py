from tutorial.code.more_complete_setup.worker.classes import Crawler
from tutorial.code.more_complete_setup.worker import tasks
from src.worker.TimeHandler import Schedule, TimeHandler
from datetime import datetime, timedelta
import src.worker.api_wrapper as api_wrapper
import json
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.parent.parent.absolute())


def single_update(date_time, experiment_id, api_token, send_queues=True):
    # Again we set the global schedule
    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)
    # Fetch the experiment we created earlier
    raw_experiment = api_wrapper.fetch_experiment(access_token=api_token,
                                                  id=experiment_id)

    # Create python objects from the json returned by the API
    crawler_list = Crawler.from_list(raw_experiment['crawlers'],
                                     date_time=date_time)
    # Assign Tasks
    for crawler in crawler_list:
        # create a queue and begin by accepting Googles cookie preferences
        session_id = crawler.add_task(tasks.HandleCookiesGoogle,
                                      to_session=True)

        if crawler.flag in {'left', 'right'} and \
                crawler.configuration.usage_type != 'only_direct':
            crawler.add_task(tasks.PoliticalSearch,
                             to_session=session_id)
        if crawler.flag in {'left', 'right'} and \
                crawler.configuration.usage_type != 'only_search':
            crawler.add_task(tasks.VisitMediaNoUtility,
                             to_session=session_id)

        crawler.add_task(tasks.GoogleSearch, to_session=session_id,
                         params={'term': 'Joe Biden'})
    t_0 = datetime.now() + timedelta(minutes=5)
    for crawler in crawler_list:
        crawler.queues[0].start_at = t_0
        t_0 + timedelta(minutes=2, seconds=30)

    with open(PRIMEMOVER_PATH + "/resources/updates/generated.json",
              'w') as file:
        json.dump(
            [crawler.as_dict(object_ids=False) for crawler in crawler_list],
            file,
            indent='  ')
    if not send_queues:
        return f'queues have been generated at {PRIMEMOVER_PATH}/resources/updates/generated.json, but not sent'
    return_data = api_wrapper.push_new(access_token=api_token,
                                       path=f'{PRIMEMOVER_PATH}/resources/updates/generated.json')
    # can only store return data if status code == 200
    if return_data.status_code == 200:
        with open(
                f'{PRIMEMOVER_PATH}/resources/updates/{date_time.date().isoformat()}.json',
                'w') as file:
            json.dump(return_data.json(), file, indent='  ')
        return 'success'
    else:
        return f'failure, code {return_data.status_code}'


if __name__ == "__main__":
    with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
        KEYS = json.load(f)
    key = api_wrapper.get_access(KEYS['PRIMEMOVER']['username'],
                                 KEYS['PRIMEMOVER']['password'])
    print(single_update(date_time =datetime.now(), experiment_id=49, api_token=key, send_queues=False))
