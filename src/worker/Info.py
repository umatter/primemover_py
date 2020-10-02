import json
import src.ConfigurationFunctions as Config

with open('resources/other/keys.json', 'r') as key_file:
    keys = json.load(key_file)
GEOSURF_USERNAME = keys['GEOSURF']['username']
GEOSURF_PASSWORD = keys['GEOSURF']['password']


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
                          finished_at = info_dict.get('finished_at')
                          )
        return info_object


class CrawlerInfo(Info):
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
            CrawlerInfo.ID += 1
            self._crawler_id = CrawlerInfo.ID

        else:
            self._crawler_id = value

    def as_dict(self):
        return {
            'id': self._crawler_id,
            'user_id': self._user_id,
            'proxy_id':self._proxy_id,
            'agent_id': self._agent_id,
            'configuration_id': self._configuration_id
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


class Agent:
    with open("resources/other/geosurf_cities.json", 'r') as file:
        LOCATION_LIST = list(json.load(file).keys())

    def __init__(self,
                 location=None,
                 name='Agent',
                 description='This is the agent',
                 identification="MultiLogin",
                 multilogin_id=None,
                 multilogin_profile=None,
                 info=None):
        self._name = name
        self._description = description
        self.location = location
        self._identification = identification
        self._multilogin_id = multilogin_id
        self._multilogin_profile = multilogin_profile
        self._info = info

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
        return_dict = {"name": self._name,
                       "description": self._description,
                       "location": self._location,
                       "identification": self._identification,
                       "multilogin_id": self._multilogin_id,
                       "multilogin_profile": self._multilogin_profile}
        if self._info is not None:
            for key, value in self._info.as_dict().items():
                return_dict['key'] = value
        return return_dict

    @classmethod
    def from_dict(cls, agent_dict):
        agent_object = cls(name=agent_dict.get('name'),
                           description=agent_dict.get('description'),
                           identification=agent_dict.get('identification'),
                           multilogin_id=agent_dict.get('multilogin_id'),
                           multilogin_profile=agent_dict.get(
                               'multilogin_profile'),
                           location=agent_dict.get('location'),
                           info=AgentInfo.from_dict(agent_dict))
        return agent_object


class ProxyInfo(Info):
    ID = 0

    def __init__(self, ID=None, user_id=None, active=1, created_at=None,
                 updated_at=None):
        self.proxy_id = ID
        super().__init__(user_id=user_id,
                         active=active,
                         created_at=created_at,
                         updated_at=updated_at)

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


class Proxy:

    def __init__(self,
                 username=GEOSURF_USERNAME,
                 password=GEOSURF_PASSWORD,
                 name="Sample Proxy",
                 description="Proxy",
                 type="GEOSURF",
                 hostname="state.geosurf.io",
                 port=8000,
                 info=None
                 ):
        self._name = name
        self._description = description
        self._type = type
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._info = info

    def as_dict(self):
        return_dict = {"name": self._name,
                       "description": self._description,
                       "type": self._type,
                       "hostname": self._hostname,
                       "port": self._port,
                       "username": self._username,
                       "password": self._password}
        if self._info is not None:
            for key, value in self._info.as_dict().items():
                return_dict['key'] = value
        return return_dict

    @classmethod
    def from_dict(cls, proxy_dict):
        proxy_object = cls(name=proxy_dict.get('name'),
                           description=proxy_dict.get('description'),
                           username=proxy_dict.get('username'),
                           password=proxy_dict.get('password'),
                           type=proxy_dict.get('type'),
                           hostname=proxy_dict.get('hostname'),
                           port=proxy_dict.get('port'),
                           info=ProxyInfo.from_dict(proxy_dict))
        return proxy_object
