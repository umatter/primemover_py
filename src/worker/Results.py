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


class SessionResult:
    def __init__(self, crawler_id=None, started_at=0,
                 success=0, failure=0,
                 created_at=None, updated_at=None, finished_at=None):
        self._crawler_id = crawler_id
        self._started_at = started_at
        self._success = success
        self._failure = failure
        self._finished_at = finished_at
        self._created_at = created_at
        self._updated_at = updated_at
