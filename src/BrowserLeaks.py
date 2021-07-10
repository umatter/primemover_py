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


def single_update(experiment_id, date=datetime.now()):
    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)

    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    raw_experiment = api_wrapper.fetch_experiment(access_token=key, id=
    experiment_id)

    crawler_list = Crawler.from_list(raw_experiment['crawlers'], date=date)
    crawler_list = UpdateObject(crawler_list, 'config')
    ids_processed = [1646, 1653, 1660, 1670, 1681, 1701, 1708, 1728, 1740, 1741,
                     1747, 1750, 1752, 1761, 1769, 1770, 1799, 1807, 1814, 1817,
                     1843, 1847, 1854, 1856, 1863, 1875,
                     1593, 1601, 1611, 1613, 1632, 1635, 1639, 1641, 1663, 1665,
                     1668, 1675, 1689, 1691, 1695, 1703, 1723, 1724, 1725, 1727,
                     1731, 1732, 1735, 1738]

    i = 0
    crawler_list_2 = []
    while len(crawler_list_2) < 50 and i < len(crawler_list):
        individual = crawler_list[i]
        if individual.crawler_info.crawler_id in ids_processed:
            i += 1
            continue
        individual.schedule = TimeHandler("US-CA-LOS_ANGELES",
                                          interval=120,
                                          wake_time=21.5 * 60 * 60,
                                          bed_time=24 * 60 * 60,
                                          date=date)
        individual.add_task(BrowserLeaks)
        crawler_list_2.append(individual)
        i += 1
    print(i)
    with open(PRIMEMOVER_PATH + "/resources/updates/generated.json",
              'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list_2], file,
                  indent='  ')

    return_data = api.push_new(access_token=key,
                               path=PRIMEMOVER_PATH + "/resources/updates/generated.json")
    data_as_dict = json.loads(return_data.text)
    with open(
            f'{PRIMEMOVER_PATH}/resources/updates/exp_2_{(date.date()).isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')


if __name__ == "__main__":
    single_update(experiment_id=41, date=datetime.now())
