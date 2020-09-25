from src.worker.ConfigureProfile import *
from src.worker.Info import Agent, Proxy, CrawlerInfo
from src.worker.TimeHandler import TimeHandler
from src.Preferences import *
from src.worker.Queue import Queue
from src.Tasks import *
import src.worker.Utilities as Util


class Crawler:
    CRAWLER_NR = 0

    def __init__(self,
                 name=None,
                 description="Crawler created through py",
                 configuration=None,
                 agent=None,
                 proxy=None,
                 active=1,
                 schedule=None,
                 testing=0,
                 crawler_info=None
                 ):
        self._description = description
        if name is None:
            self._name = f'Crawler_{Crawler.CRAWLER_NR}'
            Crawler.CRAWLER_NR += 1
        else:
            self._name = name
        self.configuration = configuration
        self.agent = agent
        if schedule is None:
            self._schedule = TimeHandler(self.agent[0].location,
                                         interval=120,
                                         bed_time=9 * 60 * 60,
                                         wake_time=7 * 60 * 60,
                                         tomorrow=True)

        else:
            self._schedule = schedule
        self.queues = {}
        self.proxy = proxy
        self.active = active
        self._testing = testing
        self._crawler_info = crawler_info

    @property
    def schedule(self):
        return self._schedule

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, config):
        if config is None:
            self._configuration = Config()
        elif type(config) is Config:
            self._configuration = config
        else:
            raise TypeError(f'configuration must be a  a  Config object')

    @property
    def agent(self):
        return self._agents

    @agent.setter
    def agent(self, agents_in):
        if agents_in is None:
            name = self._name.replace('Crawler', 'Agent')
            name = name.replace('crawler', 'agent')
            self._agents = [Agent(name=name)]
        elif type(agents_in) is list:
            check_types = [type(val) is Agent for val in agents_in]
            if False in check_types:
                raise TypeError(
                    'All entries in Agents must be of type Agent')
            else:
                self._agents = agents_in
        elif type(agents_in) is Agent:
            self._agents = [agents_in]
        else:
            raise TypeError(
                f'agents must be a list of or a single Agent object')

    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, proxies_in):
        if proxies_in is None:
            name = self._name.replace('Crawler', 'Proxy')
            name = name.replace('crawler', 'proxy')
            self._proxy = [Proxy(name=name)]
        elif type(proxies_in) is list:
            check_types = [type(val) is Proxy for val in proxies_in]
            if False in check_types:
                raise TypeError(
                    'All entries in proxies must be of type Proxy')
            else:
                self._proxy = proxies_in
        elif type(proxies_in) is Proxy:
            self._proxy = [proxies_in]
        else:
            raise TypeError(
                f'proxies must be a list of or a single Proxy object')

    def as_dict(self):
        return_dict = {
            "name": self._name,
            "description": self._description,
            "active": self.active,
            "testing": self._testing,
            "configuration": [self._configuration.as_dict()],
            "agent": [x.as_dict() for x in self.agent],
            "proxy": [x.as_dict() for x in self.proxy],
            "queues": [x.as_dict() for x in self.queues.values()]}
        if self._crawler_info is not None:
            for key, value in self._crawler_info.as_dict().items():
                return_dict['key'] = value
        return return_dict

    @classmethod
    def from_dict(cls, crawler_dict):
        if 'crawlers' in crawler_dict.keys():
            crawlers = [cls._single_crawler(ind_crawler) for
                        ind_crawler in crawler_dict['crawlers']]
        else:
            crawlers = [cls._single_crawler(crawler_dict)]
        return crawlers

    @classmethod
    def _single_crawler(cls, crawler_dict):
        proxy_object = cls(name=crawler_dict.get('name'),
                           description=crawler_dict.get('description'),
                           configuration=Config.from_dict(
                               crawler_dict['configuration']),
                           agent=Agent.from_dict(crawler_dict.get('agent')),
                           proxy=Proxy.from_dict(crawler_dict.get('proxy')),
                           crawler_info=CrawlerInfo.from_dict(crawler_dict)
                           )

        return proxy_object

    def add_task(self, cls, to_session=None, params=None, start_at=None):

        if not issubclass(cls, Queue):
            raise TypeError(f'cls must be a subclass of Queue')
        # generate new object
        if start_at is None and to_session is None or to_session is False:
            start_at = self._schedule.new_time()
        if cls.PASS_CRAWLER:
            if params is not None:
                new_queue_object = cls(crawler=self, start_at=start_at, **params)
            else:
                new_queue_object = cls(crawler=self, start_at=start_at)
        else:
            if params is not None:
                new_queue_object = cls(start_at=start_at, **params)
            else:
                new_queue_object = cls(start_at=start_at)

        # add to existing session if desired
        if to_session is not None:
            if to_session not in self.queues.keys():
                if start_at is None:
                    start_at = self._schedule.new_time()
                to_session = Util.new_key(self.queues)
                self.queues[to_session] = Queue(start_at=start_at,
                                                name=f'Session_{to_session}',
                                                delay_min=1,
                                                delay_max=10)
            self.queues[to_session] + new_queue_object
        # add to queue list as new session
        else:
            to_session = Util.new_key(self.queues)
            self.queues[to_session] = new_queue_object
        return to_session

    def add_tasks(self, cls, nr, to_session, params=None, consecutive=False,
                  time_list=None):
        if nr < 1:
            return None
        if to_session is not None:
            if to_session is not False:
                consecutive = False
        else:
            to_session = False

        if consecutive:
            time_list = self._schedule.consecutive_times(nr)

        if to_session is False:
            if time_list is not None:
                for t in time_list:
                    to_session = self.add_task(cls,params=params, start_at=t)
            else:
                for i in range(nr):
                    to_session = self.add_task(cls, params=params)
        else:
            for i in range(nr):
                to_session = self.add_task(cls,to_session=to_session, params=params)
        return to_session
