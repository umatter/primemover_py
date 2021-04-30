"""
Process results returned from primemover runner via the API
"""

import src.worker.s3_parser as Parser
from src.worker import api_wrapper
import json
from datetime import datetime, timedelta
from src.worker.Crawler import Crawler
import pathlib
import src.worker.s3_wrapper as s3
import zipfile
import io



PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
    KEYS = json.load(f)

ACCESS_TOKEN = api_wrapper.get_access(KEYS['PRIMEMOVER']['username'],
                                      KEYS['PRIMEMOVER']['password'])

class JobResult:
    """
    Stores and processes the returned data for a single job
    """

    def __init__(self, crawler_id=None, job_id=None, started_at=None,
                 status_code=None, status_message=None,
                 created_at=None, updated_at=None, finished_at=None,
                 behaviors=None, flag_list=None, reports=None,
                 parser_dict=Parser.ParserDict):
        self.crawler_id = crawler_id
        self.job_id = job_id
        self._started_at = started_at
        self.status_message = status_message
        self.status_code = status_code
        self.created_at = created_at
        self.updated_at = updated_at
        self.finished_at = finished_at
        self.task = None
        self.flag = None
        self.parsed_data = None
        self.reports = reports
        self.behaviors = behaviors
        self._extract_flags()

        self._flag_list = flag_list
        self._parser_dict = parser_dict
        self.results = None

        # Check if flag in parser dict, if yes, parse
        if self.task in self._parser_dict.keys():
            if parser_dict[self.task]['data'] == 'html':
                raw_data, success = self._download_html()
            elif parser_dict[self.task]['data'] == 'reports':
                raw_data = self.reports
                if len(self.reports > 0):
                    success = True
                else:
                    success = False
            elif parser_dict[self.task]['data'] == 'dynamic':
                raw_data, success = self._download_dynamic()
            else:
                raw_data = None
                success = True
            if success:
                self.parsed_data = self._parser_dict[self.task]['method'](
                    self.behaviors,
                    raw_data, job_id)
                self.results = {'finished_at': self.finished_at,
                                'status_code': self.status_code,
                                'status_message': self.status_message,
                                'flag': self.flag,
                                'data': self.parsed_data,
                                'job_id': self.job_id}
            else:
                self.results = {'finished_at': self.finished_at,
                                'status_code': self.status_code,
                                'status_message': self.status_message,
                                'flag': self.flag,
                                'data': None,
                                'job_id': self.job_id}
            if type(raw_data) == io.BytesIO:
                raw_data.close()

    def _download_html(self):
        raw_data, success = s3.fetch_report(self.job_id, 'static')
        if success:
            as_zipfile = zipfile.ZipFile(raw_data)

            name = None
            for name in as_zipfile.namelist():
                if 'html' in name:
                    break
            raw_html = as_zipfile.read(name)
        else:
            raw_html = None
        return raw_html, success

    def _download_dynamic(self):

        raw_data, success = s3.fetch_report(self.job_id, 'dynamic')
        if success:
            as_zipfile = zipfile.ZipFile(raw_data)
            name = None
            for name in as_zipfile.namelist():
                if 'json' in name:
                    break
            raw_json = as_zipfile.read(name)
            raw_dict = json.loads(raw_json)
        else:
            raw_dict = {}
        return raw_dict, success

    def _extract_flags(self):
        if type(self.behaviors) is list:
            for behavior in self.behaviors:
                if behavior['name'] == 'task':
                    self.task = behavior['value']
                elif behavior['name'] == 'flag':
                    self.flag = behavior['value']
                else:
                    continue

    @classmethod
    def from_list(cls, result_list, parser_dict=Parser.ParserDict):

        job_results = [cls.from_dict(ind_job, parser_dict) for ind_job in
                       result_list]

        return job_results

    @classmethod
    def from_dict(cls, result_dict, parser_dict=Parser.ParserDict):
        job_result_object = cls(crawler_id=result_dict.get('crawler_id'),
                                job_id=result_dict.get('id'),
                                started_at=result_dict.get('started_at'),
                                status_message=result_dict.get(
                                    'status_message'),
                                status_code=result_dict.get('status_code'),
                                created_at=result_dict.get('created_at'),
                                updated_at=result_dict.get('updated_at'),
                                finished_at=result_dict.get('finished_at'),
                                behaviors=result_dict.get('behaviors'),
                                reports=result_dict.get('reports'),
                                parser_dict=parser_dict)

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
                 parser_dict=Parser.ParserDict,
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
        self._parser_dict = parser_dict

        temp_results = [j.results for j in self._jobs]
        self.results = []
        for res in temp_results:
            if res is not None:
                self.results.append(res)

    @classmethod
    def from_list(cls, result_list, set_reviewed=True,
                  parser_dict=Parser.ParserDict):
        session_results = [cls.from_dict(ind_session, parser_dict=parser_dict)
                           for ind_session in
                           result_list]
        if set_reviewed:
            for sess in session_results:
                api_wrapper.set_reviewed(queue_id=sess._queue_id,
                                         access_token=ACCESS_TOKEN)

        return session_results

    @classmethod
    def from_dict(cls, result_dict, parser_dict=Parser.ParserDict):
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
                                        result_dict.get('jobs'),
                                        parser_dict=parser_dict),
                                    parser_dict=parser_dict)

        return session_result_object


def export_results(results, date=datetime.today().date().isoformat()):
    # existing_crawler_path = f'{PRIMEMOVER_PATH}/resources/updates/exp_2_{(datetime.now().date() + timedelta(days=-1)).isoformat()}.json'
    existing_crawler_path = PRIMEMOVER_PATH + '/resources/updates/test_2020-12-22.json'
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
    return combined


def process_results(set_reviewed=True, parser_dict=Parser.ParserDict,
                    path_end='', day_delta=0):
    path = f'{PRIMEMOVER_PATH}/resources/raw_data/{(datetime.now().date() + timedelta(days=day_delta)).isoformat()}.json'

    with open(path, 'r') as file:
        raw_data = json.load(file)
    session_data = SessionResult.from_list(raw_data['data'],
                                           set_reviewed=set_reviewed,
                                           parser_dict=parser_dict)

    combined_sessions = {}
    for session in session_data:
        if session.crawler_id in combined_sessions.keys():
            combined_sessions[session.crawler_id] = combined_sessions[
                                                        session.crawler_id] + session.results
        else:
            combined_sessions[session.crawler_id] = session.results

    with open(
            f'{PRIMEMOVER_PATH}/resources/cleaned_data/{path_end}{(datetime.today().date() + timedelta(days=day_delta)).isoformat()}.json',
            'w') as file:
        json.dump(combined_sessions, file, indent='  ')

    data = export_results(combined_sessions)
    return data


if __name__ == "__main__":
    date = (datetime.today().date() + timedelta(days=0)).isoformat()
    api_wrapper.fetch_results(access_token=ACCESS_TOKEN)
    process_results(set_reviewed=True, parser_dict=Parser.ParserDict,
                    path_end='all_data', day_delta=0)
    s3.upload_data(f'output/{date}.json',
                   path=f'/resources/cleaned_data/all_data{date}.json')
    process_results(set_reviewed=False, parser_dict=Parser.UpdateParser,
                    day_delta=0)
    print(date)

    # process_results(set_reviewed=True, parser_dict=Parser.UpdateParser)
    # combined_session_1 = {}
    # combined_session_2 = {}
    # for session in session_data:
    #     if "10-14" in session.start_at:
    #
    #         if session.crawler_id in combined_session_1.keys():
    #             combined_session_1[session.crawler_id] = combined_session_1[
    #                                                         session.crawler_id] + session.results
    #         else:
    #             combined_session_1[session.crawler_id] = session.results
    #     elif "10-15" in session.start_at:
    #
    #         if session.crawler_id in combined_session_2.keys():
    #             combined_session_2[session.crawler_id] = combined_session_2[
    #                                                         session.crawler_id] + session.results
    #         else:
    #             combined_session_2[session.crawler_id] = session.results
    #
    # with open(
    #         f'resources/cleaned_data/2020-10-15.json',
    #         'w') as file:
    #     json.dump(combined_session_1, file, indent='  ')
    # export_results(combined_session_1, '2020-10-1')
    #
    # with open(
    #         f'resources/cleaned_data/2020-10-16.json',
    #         'w') as file:
    #     json.dump(combined_session_2, file, indent='  ')
    # export_results(combined_session_2, date='2020-10-16')
