from tutorial.code.complete_experiment.worker.classes import Crawler
from tutorial.code.complete_experiment.worker import tasks
from src.worker.TimeHandler import Schedule, TimeHandler
from datetime import datetime, timedelta
import src.worker.api_wrapper as api_wrapper
import json
import pathlib
from src.worker import s3_wrapper
import os

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.parent.parent.absolute())


def single_update(date_time, experiment_id, api_credentials, send_queues=True,
                  fixed_times=True, delta_t_2=60, delta_t_1=120):
    api_token = api_wrapper.get_access(api_credentials.get('username'),
                               api_credentials.get('password'))

    "Fetch Neutral terms from s3 Bucket"
    neutral_path = PRIMEMOVER_PATH + '/resources/input_data/neutral_searchterms_pool.json'
    if not os.path.exists(neutral_path):
        neutral_in = s3_wrapper.fetch_neutral()
    else:
        with open(neutral_path) as file:
            neutral_in = json.load(file)
    nr_neutral = 1
    neutral = []
    if len(neutral_in) < nr_neutral:
        neutral_in += s3_wrapper.fetch_neutral()
        with open(neutral_path, 'w') as file:
            json.dump(neutral_in, file)
    for i in range(nr_neutral):
        neutral.append(neutral_in.pop(0))

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

    for c in crawler_list:
        c.schedule = TimeHandler("US-CA-LOS_ANGELES",
                                 interval=120,
                                 wake_time=18 * 60 * 60,
                                 bed_time=21 * 60 * 60,
                                 date_time=date_time)
        session_id = c.add_task(tasks.HandleCookiesGoogle,
                                to_session=True)
        c.add_task(tasks.NeutralGoogleSearch, to_session=session_id,
                   params={'term': neutral[1]})

    if fixed_times:
        queues_1 = [c.queues[0] for c in crawler_list]
        queues_1.sort(key=lambda q: datetime.fromisoformat(q.start_at))
        # t_0 = datetime.fromisoformat(queues_1[0].start_at)
        # t_0 = datetime.fromisoformat(
        #     f'{date_time.date().isoformat()}T10:00:00-06:00')
        t_0 = datetime.now() + timedelta(minutes=1)
        print(t_0)
        delta_t_1 = int(delta_t_1)
        for q in queues_1:
            q.start_at = t_0.isoformat()
            t_0 += timedelta(seconds=delta_t_1)

        queues_2 = [c.queues[1] for c in crawler_list]
        queues_2.sort(key=lambda q: datetime.fromisoformat(q.start_at))
        # t_0 = datetime.fromisoformat(
        #     f'{date_time.date().isoformat()}T21:00:00-06:00')00
        t_0 += timedelta(minutes=5)
        print(t_0)
        delta_t_2 = int(delta_t_2)
        for q in queues_2:
            q.start_at = t_0.isoformat()
            t_0 += timedelta(seconds=delta_t_2)

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

    print(single_update(date_time=datetime.now(), experiment_id=54, api_credentials=KEYS.get("PRIMEMOVER"), send_queues=True))
