from src_google.worker.classes import Crawler, Config
from src.worker import s3_wrapper, Experiment
from src_google.worker import tasks
from src.worker.UpdateObject import *
from src.worker.ReplaceProxies import update_all_proxies
from src.worker.TimeHandler import Schedule, TimeHandler
from datetime import datetime, timedelta
import src.worker.api_wrapper as api
import json
import pathlib
import os

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)


def single_update(date_time, experiment_id, manual=False, fixed_times=False, update_preferences =True,
                  update_proxies=True,
                  delta_t_1=120, delta_t_2=36):
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

    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)
    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    raw_experiment = api_wrapper.fetch_experiment(access_token=key, id=
    experiment_id)

    crawler_list = Crawler.from_list(raw_experiment['crawlers'],
                                             date_time=date_time)
    crawler_list = UpdateObject(crawler_list, Config)
    "Compute Proxy Changes"
    if update_proxies:
        update_proxies_dict = update_all_proxies()
        crawler_list = [
            crawler.update_crawler(proxy_update=update_proxies_dict) for crawler in crawler_list]
    crawler_list_neutral = []
    crawler_list_political = []
    for crawler in crawler_list:
        if crawler.flag in {'right', 'left'}:
            crawler_list_political.append(crawler)
        else:
            crawler_list_neutral.append(crawler)
    if update_preferences:
        if os.path.exists(
                f'{PRIMEMOVER_PATH}/resources/cleaned_data/{date_time.date().isoformat()}.json'):
            with open(
                    f'{PRIMEMOVER_PATH}/resources/cleaned_data/{date_time.date().isoformat()}.json',
                    'r') as file:
                cleaned_data = json.load(file)
            crawler_list_political = [
                crawler.update_crawler(results=cleaned_data) for crawler
                in crawler_list_political]

    crawler_list = crawler_list_political + crawler_list_neutral

    for individual in crawler_list:
        session_id = individual.add_task(tasks.HandleCookiesGoogle,
                                         to_session=True)
        session_id = individual.add_task(tasks.SetGooglePreferences,
                                         to_session=session_id,
                                         params={'nr_results': 30, 'set_language': "English"})
        if individual.flag in {'left', 'right'} and \
                individual.configuration.usage_type in {'only_search', 'both',
                                                        None}:
            individual.add_task(tasks.PoliticalSearch,
                                to_session=session_id)
            # individual.add_task(tasks.PoliticalSearch,
            #                     to_session=session_id)
        if individual.flag in {'left', 'right'} and \
                individual.configuration.usage_type in {'only_direct', 'both',
                                                        None}:
            individual.add_task(tasks.VisitMedia,
                                to_session=session_id)
            # individual.add_task(tasks.VisitMedia,
            #                     to_session=session_id)

        if individual.configuration.usage_type in {'only_direct', 'both', None}:
            individual.add_task(tasks.VisitNeutralDirect,
                                to_session=session_id)
            individual.add_task(tasks.VisitNeutralDirect,
                                to_session=session_id)

        individual.add_task(tasks.NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[0]})

    for c in crawler_list:
        c.schedule = TimeHandler("US-CA-LOS_ANGELES",
                                 interval=120,
                                 wake_time=18 * 60 * 60,
                                 bed_time=21 * 60 * 60,
                                 date_time=date_time)
        session_id = c.add_task(tasks.HandleCookiesGoogle,
                                to_session=True)
        c.add_task(tasks.NeutralGoogleSearch, to_session=session_id,
                   params={'term': neutral[0]})
        # c.add_task(tasks.NeutralGoogleSearch, to_session=session_id,
        #            params={'term': neutral[1]})
    if fixed_times:
        crawler_list = crawler_list[0:1]
        queues_1 = [c.queues[0] for c in crawler_list]
        queues_1.sort(key=lambda q: datetime.fromisoformat(q.start_at))
        # t_0 = datetime.fromisoformat(queues_1[0].start_at)
        # t_0 = datetime.fromisoformat(
        #     f'{date_time.date().isoformat()}T10:00:00-06:00')
        t_0 = datetime.now() + timedelta(minutes=1)
        print(t_0)
        delta_t_1 = int(delta_t_1)
        for q in queues_1[0:]:
            q.start_at = t_0.isoformat()
            t_0 += timedelta(seconds=delta_t_1)

        queues_2 = [c.queues[1] for c in crawler_list]
        queues_2.sort(key=lambda q: datetime.fromisoformat(q.start_at))
        # t_0 = datetime.fromisoformat(
        #     f'{date_time.date().isoformat()}T21:00:00-06:00')00
        t_0 += timedelta(minutes=5)
        print(t_0)
        delta_t_2 = int(delta_t_2)
        for q in queues_2[0:]:
            q.start_at = t_0.isoformat()
            t_0 += timedelta(seconds=delta_t_2)

    with open(PRIMEMOVER_PATH + "/resources/updates/generated.json",
              'w') as file:
        json.dump(
            [crawler.as_dict(object_ids=False) for crawler in crawler_list],
            file,
            indent='  ')
    # Create complete copy of crawlers
    for c in crawler_list:
        c.send_agent = True

    with open(PRIMEMOVER_PATH + "/resources/updates/complete.json",
              'w') as file:
        json.dump(
            [crawler.as_dict(object_ids=True) for crawler in crawler_list],
            file,
            indent='  ')

    if manual:
        do = input('push data? (y/n): ')
    else:
        do = 'y'

    message = 'success'
    error_code = None
    if do == 'y':

        return_data = api.push_new(access_token=key,
                                   path=f'{PRIMEMOVER_PATH}/resources/updates/generated.json')
        if return_data.status_code == 200:
            with open(
                    f'{PRIMEMOVER_PATH}/resources/updates/{date_time.date().isoformat()}.json',
                    'w') as file:
                json.dump(return_data.json(), file, indent='  ')
            # Delete neutral terms if push was successful
            with open(neutral_path, 'w') as file:
                json.dump(neutral_in, file)
        else:
            message = {return_data.text}
            error_code = return_data.content
            print(return_data)

        # experiment = api.update_experiment(key, [exp.as_dict()], exp.id)
    # print(experiment)
    try:
        with open(PRIMEMOVER_PATH + f'/resources/log/log_{date_time.date().isoformat()}.json', 'r') as f:
            log = json.load(f)
    except FileNotFoundError:
        log = {"Tasks": {}}
    with open(PRIMEMOVER_PATH + f'/resources/log/log_{date_time.date().isoformat()}.json', 'w') as f:
        log["Tasks"]["Update_Crawler"] = message
        if error_code is not None:
            log["Update_error"] = error_code
        json.dump(log, f, indent='  ')


if __name__ == "__main__":
    # for day in range(13):
    #     single_update(day_delta=day)
    #     print((datetime.now().date() + timedelta(days=day)).isoformat())
    single_update(date_time=datetime.now(),
                  experiment_id=48,
                  manual=True,
                  update_preferences=False,
                  update_proxies=False,
                  fixed_times=True,
                  delta_t_1=240, delta_t_2=60)
