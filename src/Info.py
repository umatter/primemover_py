import json
import src.ConfigurationFunctions as Config


class Info:
    def __init__(self, user_id=None, active=1, created_at=None,
                 updated_at=None):
        self._user_id = user_id
        self.active = active
        self.updated_at = created_at
        self.created_at = updated_at


class BehaviorInfo(Info):
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
    ID = 0

    def __init__(self, ID=None, user_id=None, queue_id=None, started=0,
                 sucess=0, failure=0, timeout=0, order=1, active=1,
                 created_at=None, updated_at=None):
        self.queue_id = queue_id
        self.job_id = ID
        self.started = started
        self.success = sucess
        self.failure = failure
        self.timeout = timeout
        self.order = order
        super().__init__(user_id=user_id, active=active, created_at=created_at,
                         updated_at=updated_at)

    def new_behavior(self):
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


class QueueInfo(Info):
    ID = 0

    def __init__(self, ID=None, user_id=None, crawler_id=None, started=0,
                 sucess=0, failure=0, timeout=0, order=1, active=1,
                 created_at=None, updated_at=None):
        self.queue_id = ID
        self.crawler_id = crawler_id
        self.started = started
        self.success = sucess
        self.failure = failure
        self.timeout = timeout
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


class CrawlerInfo(Info):
    ID = 0

    def __init__(self, ID=None, user_id=None, agent_id=None, proxy_id=None,
                 configuration_id=None, active=1, created_at=None,
                 updated_at=None):
        self.crawler_id = ID
        self.agent_id = agent_id
        self.proxy_id = proxy_id
        self.configuration_id = configuration_id
        super().__init__(user_id=user_id, active=active, created_at=created_at,
                         updated_at=updated_at)

    @property
    def crawler_id(self):
        return self._crawler_id

    @crawler_id.setter
    def crawler_id(self, value):
        if value is None:
            CrawlerInfo.ID += 1
            self._crawler_id = CrawlerInfo.ID

        else:
            self._crawler_id = value

    def new_queue(self):
        return QueueInfo(user_id=self._user_id, crawler_id=self.crawler_id)


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
                           configuration_id=self.configuration_id)


class Agent:
    with open("resources/other/geosurf_cities.json", 'r') as file:
        LOCATION_LIST = list(json.load(file).keys())

    def __init__(self,
                 location=None,
                 name=None,
                 description=None,
                 identification=None,
                 multilogin_id=None,
                 multilogin_profile=None):
        self._name = name
        self._description = description
        self.location = location
        self._identification = identification
        self._multilogin_id = multilogin_id
        self._multilogin_profile = multilogin_profile

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, val):
        if val is None:
            self._location = Config.location()
        elif val in Agent.LOCATION_LIST:
            self._location = val
        else:
            raise ValueError(
                f'{val} is not a valid location see geosurf cities')

    def as_dict(self):
        return {"name": self._name,
                "description": self._description,
                "location": self._location,
                "identification": self._identification,
                "multilogin_id": self._multilogin_id,
                "multilogin_profile": self._multilogin_profile}


class Proxy:

    def __init__(self,
                 name="Sample Proxy",
                 description="Placeholder proxy",
                 type="HTTP",
                 hostname="localhost",
                 port=8080,
                 username="admin",
                 password="admin12345"):
        self._name = name
        self._description = description
        self._type = type
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password

    def as_dict(self):
        return {"name": self._name,
                "description": self._description,
                "type": self._type,
                "hostname": self._hostname,
                "port": self._port,
                "username": self._username,
                "password": self._password}
