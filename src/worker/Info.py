"""
Basic info objects for the major components of primemover_py.
These contain user and id information. This information is first assigned
by the primemover API and can then be used by primemover_py for analysis or to
identify objects on the API.

Classes:
    Info: basic info object
    BehaviorInfo: Info object for the Behavior class (Behavior.py)
    JobInfo: Info object for the Job class (Jobs.py)
    QueueInfo: Info object for the Queue class (Queue.py)
    CrawlerInfo: Info object for the Crawler class (Crawler.py)
    ConfigurationInfo: Info object for the Configuration class (ConfigurationProfile.py)
    AgentInfo: Info object for the Agent class (Agent.py)
    ProxyInfo: Info object for the Proxy class (Proxy.py)

J.L 11/2020
"""

import json


class Info:
    """
    Base class
    Public Arguments:
        - active: {0,1}, default: 1
        - updated_at: timestamp for last update on API
        - created_at: timestamp for creation on API
    """

    def __init__(self, user_id=None, active=1, created_at=None,
                 updated_at=None):
        self._user_id = user_id
        self.active = active
        self.updated_at = created_at
        self.created_at = updated_at


class BehaviorInfo(Info):
    """
    Info class for Behavior objects
    Public Arguments:
        - job_id: unique job_id, indicates which job the behavior is a part of.
        - behavior_id
        - active: {0,1}, default: 1
        - updated_at: timestamp for last update on AP
        - created_at: timestamp for creation on API
    """
    ID = 0

    def __init__(self, ID=None, user_id=None, job_id=None, active=1,
                 created_at=None, updated_at=None):
        self.job_id = job_id
        self.behavior_id = ID
        super().__init__(user_id=user_id, active=active, created_at=created_at,
                         updated_at=updated_at)

    @property
    def behavior_id(self):
        return self._behavior_id

    @behavior_id.setter
    def behavior_id(self, value):
        if value is None:
            BehaviorInfo.ID += 1
            self._behavior_id = BehaviorInfo.ID
        else:
            self._behavior_id = value


class JobInfo(Info):
    """
    OUTDATED AND NOT IN USE
    Info class for Job objects
    Public Arguments:
        - queue: unique queue id, indicates which queue the job is a part of.
        - job_id: unique ID of the job
        - active: {0,1}, default: 1
        - updated_at: timestamp for last update on AP
        - created_at: timestamp for creation on API
        - start_at: Time stamp at which primemover runner began executing the job
        - success: {1,0} 1=Success
        - failure: {1,0} 1 = Failure
    """
    ID = 0

    def __init__(self, ID=None, user_id=None, queue_id=None, started_at=0,
                 sucess=0, failure=0, timeout=0, order=1, active=1,
                 created_at=None, updated_at=None):
        self.queue_id = queue_id
        self.job_id = ID
        self.started_at = started_at
        self.success = sucess
        self.failure = failure
        self.timeout = timeout
        self.order = order
        super().__init__(user_id=user_id, active=active, created_at=created_at,
                         updated_at=updated_at)

    def new_behavior(self):
        """
        legacy: generates a new Behavior, id will not match API Ids!!
        """
        return BehaviorInfo(user_id=self._user_id, job_id=self.job_id)

    @property
    def job_id(self):
        return self._job_id

    @job_id.setter
    def job_id(self, value):
        if value is None:
            JobInfo.ID += 1
            self._job_id = JobInfo.ID
        else:
            self._job_id = value

    @classmethod
    def from_dict(cls, info_dict):
        info_object = cls(info_dict.get('id'),
                          user_id=info_dict.get('user_id'),
                          queue_id=info_dict.get('queue_id'),
                          started_at=info_dict.get('started_at'),
                          sucess=info_dict.get('sucess'),
                          failure=info_dict.get('failure'),
                          order=info_dict.get('order'),
                          created_at=info_dict.get('created_at'),
                          updated_at=info_dict.get('updated_at'),
                          active=info_dict.get('active')
                          )
        return info_object


class QueueInfo(Info):
    """OUTDATED AND NOT IN USE"""
    ID = 0

    def __init__(self, ID=None, user_id=None, crawler_id=None, started_at=0,
                 sucess=0, failure=0, order=1, active=1,
                 created_at=None, updated_at=None, finished_at=None):
        self.queue_id = ID
        self.crawler_id = crawler_id
        self.started_at = started_at
        self.success = sucess
        self.failure = failure
        self.finished_at = finished_at
        self.order = order
        super().__init__(user_id=user_id, active=active, created_at=created_at,
                         updated_at=updated_at)

    def new_job(self):
        return JobInfo(user_id=self._user_id, queue_id=self.queue_id)

    @property
    def queue_id(self):
        return self._queue_id

    @queue_id.setter
    def queue_id(self, value):
        if value is None:
            QueueInfo.ID += 1
            self._queue_id = QueueInfo.ID
        else:
            self._queue_id = value

    @classmethod
    def from_dict(cls, info_dict):
        info_object = cls(info_dict.get('id'),
                          user_id=info_dict.get('user_id'),
                          crawler_id=info_dict.get('crawler_id'),
                          started_at=info_dict.get('started_at'),
                          sucess=info_dict.get('sucess'),
                          failure=info_dict.get('failure'),
                          order=info_dict.get('order'),
                          created_at=info_dict.get('created_at'),
                          updated_at=info_dict.get('updated_at'),
                          active=info_dict.get('active'),
                          finished_at=info_dict.get('finished_at')
                          )
        return info_object


class CrawlerInfo(Info):
    """
    Info class for Crawler objects
    Public Arguments:
        - crawler_id: unique crawler ID
        - configuration_id: identifies the corresponding configuration file
        - agent_id: identifies the corresponding agent file
        - proxy_id: identifies the corresponding proxy file
        - active: {0,1}, default: 1
        - updated_at: timestamp for last update on AP
        - created_at: timestamp for creation on API
    """
    ID = 0

    def __init__(self, ID=None, user_id=None, agent_id=None, proxy_id=None,
                 configuration_id=None, active=1, created_at=None,
                 updated_at=None):
        self.crawler_id = ID
        self._agent_id = agent_id
        self._proxy_id = proxy_id
        self._configuration_id = configuration_id
        super().__init__(user_id=user_id, active=active, created_at=created_at,
                         updated_at=updated_at)

    @property
    def crawler_id(self):
        return self._crawler_id

    @crawler_id.setter
    def crawler_id(self, value):
        if value is None:
            # CrawlerInfo.ID += 1
            # self._crawler_id = CrawlerInfo.ID
            self._crawler_id = None

        else:
            self._crawler_id = value

    def as_dict(self):
        return {
            'id': self._crawler_id,
            'user_id': self._user_id
        }

    def new_queue(self):
        return QueueInfo(user_id=self._user_id, crawler_id=self.crawler_id)

    @classmethod
    def from_dict(cls, info_dict):
        info_object = cls(info_dict.get('id'), user_id=info_dict.get('user_id'),
                          agent_id=info_dict.get('agent_id'),
                          proxy_id=info_dict.get('proxy_id'),
                          configuration_id=info_dict.get('configuration_id'),
                          created_at=info_dict.get('created_at'),
                          updated_at=info_dict.get('updated_at'),
                          active=info_dict.get('active')
                          )
        return info_object


class ConfigurationInfo(Info):
    ID = 0

    def __init__(self, ID=None, user_id=None, active=1, created_at=None,
                 updated_at=None):
        self.configuration_id = ID
        super().__init__(user_id=user_id,
                         active=active,
                         created_at=created_at,
                         updated_at=updated_at)

    @property
    def configuration_id(self):
        return self._configuration_id

    @configuration_id.setter
    def configuration_id(self, value):
        if value is None:
            ConfigurationInfo.ID += 1
            self._configuration_id = ConfigurationInfo.ID

        else:
            self._configuration_id = value

    def new_crawler(self):
        return CrawlerInfo(user_id=self._user_id,
                           configuration_id=self.configuration_id, )

    def as_dict(self):
        return {
            'id': self._configuration_id,
            'user_id': self._user_id,
        }

    @classmethod
    def from_dict(cls, info_dict):
        info_object = cls(info_dict.get('id'),
                          user_id=info_dict.get('user_id'),
                          created_at=info_dict.get('created_at'),
                          updated_at=info_dict.get('updated_at'),
                          active=info_dict.get('active'))
        return info_object


class AgentInfo(Info):
    ID = 0

    def __init__(self, ID=None, user_id=None, active=1, created_at=None,
                 updated_at=None):
        self.agent_id = ID
        super().__init__(user_id=user_id,
                         active=active,
                         created_at=created_at,
                         updated_at=updated_at)

    def as_dict(self):
        return {
            'id': self._agent_id,
            'user_id': self._user_id,
        }

    @property
    def agent_id(self):
        return self._agent_id

    @agent_id.setter
    def agent_id(self, value):
        if value is None:
            AgentInfo.ID += 1
            self._agent_id = AgentInfo.ID
        else:
            self._agent_id = value

    @classmethod
    def from_dict(cls, info_dict):
        info_object = cls(info_dict.get('id'),
                          user_id=info_dict.get('user_id'),
                          created_at=info_dict.get('created_at'),
                          updated_at=info_dict.get('updated_at'),
                          active=info_dict.get('active'))
        return info_object


class ProxyInfo(Info):
    ID = 0

    def __init__(self, ID=None, user_id=None, active=1, created_at=None,
                 updated_at=None):
        self.proxy_id = ID
        super().__init__(user_id=user_id,
                         active=active,
                         created_at=created_at,
                         updated_at=updated_at)

    def as_dict(self):
        return {
            'id': self._proxy_id,
            'user_id': self._user_id,
        }

    @property
    def proxy_id(self):
        return self._proxy_id

    @proxy_id.setter
    def proxy_id(self, value):
        if value is None:
            ProxyInfo.ID += 1
            self._proxy_id = ProxyInfo.ID
        else:
            self._proxy_id = value

    @classmethod
    def from_dict(cls, info_dict):
        info_object = cls(info_dict.get('id'),
                          user_id=info_dict.get('user_id'),
                          created_at=info_dict.get('created_at'),
                          updated_at=info_dict.get('updated_at'),
                          active=info_dict.get('active'))
        return info_object
