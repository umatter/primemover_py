from datetime import datetime
import json
from src.worker import api_wrapper as api
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)

key = api.get_access(KEYS['PRIMEMOVER']['username'],
                     KEYS['PRIMEMOVER']['password'])
try:
    res = api.fetch_results(key, 36)['data']
except FileExistsError:
    path = f'{PRIMEMOVER_PATH}/resources/raw_data/{datetime.now().date().isoformat()}.json'

    with open(path, 'r') as file:
        res = json.load(file)
    res = res['data']

def to_datetime(time_str):
    tz = time_str[-5:]
    if tz[0] == '+':
        time_str = time_str[:-2] + ':' + time_str[-2:]
    return datetime.fromisoformat(time_str)


all_times = [to_datetime(r['start_at']) for r in res]
all_times.sort()
deltas = []
running_sum = []
for i, t in enumerate(all_times[1:]):
    deltas.append((t - all_times[i]).total_seconds())
    running_sum.append(sum(deltas))

failure = []
failure_times = []
success = []
for r in res:
    if r['status_code'] == 'success':
        success.append({'crawler_id':r['crawler_id'], 'queue_id':r['id']})
    else:
        failure.append(
            r['crawler_id'])
        failure_times.append(to_datetime(r['start_at']))

failure_times.sort()
deltas_failure = []
for i, t in enumerate(failure_times[1:]):
    deltas_failure.append((t - failure_times[i]).total_seconds())

for j,t in enumerate(deltas):
    if t == 69.231077:
        print(j)


deltas_started = []
all_times_started = [to_datetime(r['started_at']) for r in res]
all_times_started.sort()
running_sum_started = []
for i, t in enumerate(all_times_started[1:]):
    deltas_started.append((t - all_times_started[i]).total_seconds())
    running_sum_started.append(sum(deltas_started))
