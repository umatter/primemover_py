from src.worker.Behavior import TaskBehavior, FlagBehavior


class JobResult:
    def __init__(self, crawler_id=None, started_at=0,
                 success=0, failure=0,
                 created_at=None, updated_at=None, finished_at=None,
                 behaviors=None, reports=None):
        self._crawler_id = crawler_id
        self._started_at = started_at
        self._success = success
        self._failure = failure
        self._finished_at = finished_at
        self._created_at = created_at
        self._updated_at = updated_at

        self._task = None
        self._flag = None

        self._behaviors = behaviors
        self._extract_flags()

        self._reports = reports

    def _extract_flags(self):
        if type(self._behaviors) is list:
            for behavior in self._behaviors:
                if type(behavior) is TaskBehavior:
                    self._task = behavior.value
                elif type(behavior) is FlagBehavior:
                    self._flag = behavior.value
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
                                success=result_dict.get('success'),
                                failure=result_dict.get('failure'),
                                created_at=result_dict.get('created_at'),
                                updated_at=result_dict.get('updated_at'),
                                finished_at=result_dict.get('finished_at'),
                                behaviors=result_dict.get('behaviors'),
                                reports=result_dict.get('reports'))

        return job_result_object


class SessionResult:
    def __init__(self, crawler_id=None, started_at=0,
                 success=0, failure=0,
                 created_at=None, updated_at=None, finished_at=None, jobs=None):
        self._crawler_id = crawler_id
        self._started_at = started_at
        self._success = success
        self._failure = failure
        self._finished_at = finished_at
        self._created_at = created_at
        self._updated_at = updated_at

    @classmethod
    def from_dict(cls, result_dict):
        session_result_object = cls(crawler_id=result_dict.get('crawler_id'),
                                    started_at=result_dict.get('started_at'),
                                    success=result_dict.get('success'),
                                    failure=result_dict.get('failure'),
                                    created_at=result_dict.get('created_at'),
                                    updated_at=result_dict.get('updated_at'),
                                    finished_at=result_dict.get('finished_at'),
                                    jobs=JobResult.from_list(result_dict.get('jobs')))

        return session_result_object
