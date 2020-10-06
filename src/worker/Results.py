from src.Parser import *
from src.worker import api_wrapper
import json
from datetime import datetime


class JobResult:
    def __init__(self, crawler_id=None, started_at=None,
                 status_code=None, status_message=None,
                 created_at=None, updated_at=None, finished_at=None,
                 behaviors=None, reports=None):
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

        if self._task in ParserDict.keys() and len(self._reports) > 0:
            raw_data = self._download_reports()
            self._parsed_data = ParserDict[self._task](raw_data)
            self.results = {'finished_at': self._finished_at,
                            'status_code': self._status_code,
                            'status_message': self._status_message,
                            'flag': self._flag, 'data': self._parsed_data}
        else:
            self.results = None

    def _download_reports(self):
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
    def from_list(cls, result_list):
        session_results = [cls.from_dict(ind_session) for ind_session in
                           result_list]
        set_reviewed = []
        for session in session_results:
            if session._reviewed == 0:
                set_reviewed.append(session._queue_id)

        return session_results, set_reviewed

    @classmethod
    def from_dict(cls, result_dict):
        session_result_object = cls(crawler_id=result_dict.get("crawler_id"),
                                    started_at=result_dict.get("started_at"),
                                    queue_id=result_dict.get("queue_id"),
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


if __name__ == "__main__":
    path = f'resources/raw_data/{datetime.today().date().isoformat()}.json'
    with open(path, 'r') as file:
        raw_data = json.load(file)
    session_data, to_set_review = SessionResult.from_list(raw_data['data'])

    combined_sessions = {}
    for session in session_data:
        if session.crawler_id in combined_sessions.keys():
            combined_sessions[session.crawler_id] = combined_sessions[
                                                        session.crawler_id] + session.results
        else:
            combined_sessions[session.crawler_id] = session.results

    with open(
            f'resources/cleaned_data/{datetime.today().date().isoformat()}.json',
            'w') as file:
        json.dump(combined_sessions, file, indent='  ')
