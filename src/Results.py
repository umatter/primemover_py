"""
Process results returned from primemover runner via the API
"""

from src.worker.Parser import *
from src.worker import api_wrapper
import json
from datetime import datetime, timedelta
from src.worker.Crawler import Crawler
import pathlib
import os

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())


class JobResult:
    """
    Stores and processes the returned data for a single job
    """

    def __init__(self, crawler_id=None, started_at=None,
                 status_code=None, status_message=None,
                 created_at=None, updated_at=None, finished_at=None,
                 behaviors=None, reports=None, flag_list=None):
        self._crawler_id = crawler_id
        self._started_at = started_at
        self._status_message = status_message
        self._status_code = status_code
        self._created_at = created_at
        self._updated_at = updated_at
        self._finished_at = finished_at
        self._task = None
        self._flag = None
        self._parsed_data = None

        self._behaviors = behaviors
        self._extract_flags()
        self._reports = reports

        self._flag_list = flag_list

        # Check if flag in parser dict, if yes, parse
        if self._task in ParserDict.keys():
            if len(self._reports) > 0:
                if ParserDict[self._task]['data'] == 'html':
                    raw_data = self._download_html()
                elif ParserDict[self._task]['data'] == 'reports':
                    raw_data = self._reports
                else:
                    raw_data = None
                self._parsed_data = ParserDict[self._task]['method'](
                    self._behaviors,
                    raw_data)
                self.results = {'finished_at': self._finished_at,
                                'created_at': self._created_at,
                                'status_code': self._status_code,
                                'status_message': self._status_message,
                                'flag': self._flag,
                                'data': self._parsed_data,
                                'reports': self._reports}
            else:
                self._parsed_data = ParserDict[self._task]['method'](
                    self._behaviors, None)
                self.results = {'finished_at': self._finished_at,
                                'status_code': self._status_code,
                                'status_message': self._status_message,
                                'flag': self._flag,
                                'data': self._parsed_data,
                                'reports': self._reports}

        else:
            self.results = None

    def _download_html(self):
        raw_data = []
        for report in self._reports:
            raw_data.append(api_wrapper.fetch_html(report['path']))
        return raw_data

    def _extract_flags(self):
        if type(self._behaviors) is list:
            for behavior in self._behaviors:
                if behavior['name'] == 'task':
                    self._task = behavior['value']
                elif behavior['name'] == 'flag':
                    self._flag = behavior['value']
                else:
                    continue

    @classmethod
    def from_list(cls, result_list):

        job_results = [cls.from_dict(ind_job) for ind_job in result_list]

        return job_results

    @classmethod
    def from_dict(cls, result_dict):
        job_result_object = cls(crawler_id=result_dict.get('crawler_id'),
                                started_at=result_dict.get('started_at'),
                                status_message=result_dict.get(
                                    'status_message'),
                                status_code=result_dict.get('status_code'),
                                created_at=result_dict.get('created_at'),
                                updated_at=result_dict.get('updated_at'),
                                finished_at=result_dict.get('finished_at'),
                                behaviors=result_dict.get('behaviors'),
                                reports=result_dict.get('reports'))

        return job_result_object


class SessionResult:
    def __init__(self, crawler_id=None,
                 queue_id=None,
                 name=None,
                 description=None,
                 active=None,
                 processed=None,
                 reviewed=None,
                 status_code=None,
                 status_message=None,
                 order=None,
                 start_at=None,
                 updated_at=None,
                 created_at=None,
                 started_at=None,
                 finished_at=None,
                 user_id=None,
                 jobs=None,
                 ):
        self.crawler_id = crawler_id
        self._started_at = started_at
        self._queue_id = queue_id
        self._name = name
        self._description = description
        self._active = active
        self._processed = processed
        self._reviewed = reviewed
        self._status_code = status_code
        self._status_message = status_message
        self._order = order
        self._start_at = start_at
        self._finished_at = finished_at
        self._created_at = created_at
        self._updated_at = updated_at
        self._user_id = user_id
        self._jobs = jobs

        temp_results = [j.results for j in self._jobs]
        self.results = []
        for res in temp_results:
            if res is not None:
                self.results.append(res)

    @classmethod
    def from_list(cls, result_list, set_reviewed=True):
        session_results = [cls.from_dict(ind_session) for ind_session in
                           result_list]
        if set_reviewed:
            for sess in session_results:
                api_wrapper.set_reviewed(sess._queue_id)

        return session_results

    @classmethod
    def from_dict(cls, result_dict):
        session_result_object = cls(crawler_id=result_dict.get("crawler_id"),
                                    started_at=result_dict.get("started_at"),
                                    queue_id=result_dict.get("id"),
                                    name=result_dict.get("name"),
                                    description=result_dict.get("description"),
                                    active=result_dict.get("active"),
                                    processed=result_dict.get("processed"),
                                    reviewed=result_dict.get("reviewed"),
                                    status_code=result_dict.get("status_code"),
                                    status_message=result_dict.get(
                                        "status_message"),
                                    order=result_dict.get("order"),
                                    start_at=result_dict.get("start_at"),
                                    finished_at=result_dict.get("finished_at"),
                                    created_at=result_dict.get("created_at"),
                                    updated_at=result_dict.get("updated_at"),
                                    user_id=result_dict.get("user_id"),
                                    jobs=JobResult.from_list(
                                        result_dict.get('jobs')))

        return session_result_object


def export_results(results, date=datetime.today().date().isoformat()):
    # existing_crawler_path = f'{PRIMEMOVER_PATH}/resources/updates/exp_2_{(datetime.now().date() + timedelta(days=-1)).isoformat()}.json'
    existing_crawler_path = PRIMEMOVER_PATH + '/resources/updates/exp_2_2020-11-08.json'
    out_path = f'{PRIMEMOVER_PATH}/resources/cleaned_data/with_crawler_{date}.json'
    with open(existing_crawler_path, 'r') as file:
        crawlers = Crawler.from_dict(json.load(file))
    combined = []
    for crawler in crawlers:
        crawler_dict = crawler.as_dict()
        key = crawler_dict['id']
        crawler_dict['results'] = results.get(key)
        combined.append(crawler_dict)
    with open(out_path, 'w') as file:
        json.dump(combined, file, indent='  ')


def process_results(set_reviewed=True, date=(
        datetime.now().date() + timedelta(days=0)).isoformat()):
    path = f'{PRIMEMOVER_PATH}/resources/raw_data/{date}.json'
    with open(path, 'r') as file:
        raw_data = json.load(file)
    session_data = SessionResult.from_list(raw_data['data'],
                                           set_reviewed=set_reviewed)

    combined_sessions = {}
    for session in session_data:
        if session.crawler_id in combined_sessions.keys():
            combined_sessions[session.crawler_id] = combined_sessions[
                                                        session.crawler_id] + session.results
        else:
            combined_sessions[session.crawler_id] = session.results

    with open(
            f'{PRIMEMOVER_PATH}/resources/cleaned_data/{date}.json',
            'w') as file:
        json.dump(combined_sessions, file, indent='  ')

    export_results(combined_sessions, date=date)
    return 'success'


def results_interactive():
    y_n = input('Fetch new Data?: (y/n) ')
    if y_n == 'y':
        api_wrapper.fetch_results()
        date = (datetime.now().date() + timedelta(days=0)).isoformat()
        y_n = input('Set reviewed?: (y/n) ')
        process_results(set_reviewed=y_n == 'y', date=date)

    y_n = input(
        'Re-process existing files from scratch? This WILL overwrite cleaned Files: (y/n) ')
    if y_n == 'y':
        nr_days = int(input(
            'How many days back would you like to process? (More is not an issue): '))
        for days_ago in range(0, nr_days):
            date = (datetime.now().date() + timedelta(
                days=-days_ago)).isoformat()
            print(f'Now processing data for the {date}')

            if os.path.exists(
                    f'{PRIMEMOVER_PATH}/resources/raw_data/{date}.json'):
                process_results(set_reviewed=False, date=date)

    y_n = input(
        'Prrocess existing raw data for which no cleaned file exists? This WILL NOT overwrite cleaned Files: (y/n) ')
    if y_n == 'y':
        nr_days = int(input(
            'How many days back would you like to process? (More is not an issue): '))
        for days_ago in range(0, nr_days):
            date = (datetime.now().date() + timedelta(
                days=-days_ago)).isoformat()
            print(f'Now processing data for the {date}')
            if not os.path.exists(
                    f'{PRIMEMOVER_PATH}/resources/raw_data/{date}.json'):
                continue
            if not os.path.exists(f'{PRIMEMOVER_PATH}/resources/cleaned_data/{date}.json'):
                process_results(set_reviewed=False, date=date)


if __name__ == "__main__":
    results_interactive()
