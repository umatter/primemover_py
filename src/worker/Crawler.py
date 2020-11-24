"""
This module contains the Crawler class. The crawler class can be used to combine
configurations, proxy and agent information and schedule new tasks, potentially
based on this information. This can then be exported and pushed to the primemover_api

J.L. 11.2020
"""

from src.worker.ConfigureProfile import Config
from src.worker.Info import CrawlerInfo
from src.worker.Agent import Agent
from src.worker.Proxy import Proxy
from src.worker.TimeHandler import TimeHandler
import src.worker.Utilities as Util
import src.worker.Tasks as Tasks


class Crawler:
    """ Crawler combines all relevant information about an individual bot. It contains
    configuration, proxy, agent, queue (task) data and the necessary information
    to re-identify a crawler both in the primemover_api and in primemover_py.

    Public arguments:
        - name: string, optional but recomended, can be used to store information for processing
            passing  <<some_name>>/<<flag>> will set the flag parameter if none is set.
        - description: string, optional
        - configuration: a configuration object.
            default: generates a new config object with all parameters determined
            through ConfigurationFunctions or defaults. The name defaults to a modified version of the crawler name.
        - agent: Agent object
            default: generates default Agent object
        - proxy: Proxy object
            default: generates default Proxy object
        - active: {1,0} if 0, a pushed version of this crawler will not be run.
            default: 1
        - schedule: TimeHandler object, best practice is to pass a TimeHandler object when it deviates from the preset.
            Do not be tempted to meddle in the crawler file. Changes tend to be forgotten, causing issues in execution on the runner.
            This parameter controls scheduling of tasks for the runner. Be aware that the global_schedule should be configured.
            default: 9pm-4am, in local timezone, with min. 120 second intervals.
        - testing: {1,0} if 1, a pushed version of this crawler is seen separately from others.
            default: 0
        - crawler_info: CrawlerInfo object (optional) if one is passed, this is output and can be used by the API
            to overwrite an existing crawler on the API
        - flag: set a flag for the crawler. This will be added to the name. Only pass if no flag is passed as part of the name,
            ideally pass a name or a flag.
        - experiment_id: int, (in development)
        - day_delta: set tasks to be executed on different day. This can be used to itterate into the future easily.

    Public methods:
        - add_task: add a single task for the crawler to execute
        - add_tasks: add multiple tasks for the crawler to execute
        - clear day: empty queues (best not use, as time handler object is not overwritten.)
    """

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
                 crawler_info=None,
                 flag=None,
                 experiment_id=None,
                 day_delta=0
                 ):
        self.flag = flag
        self._description = description
        if name is None:
            if self.flag is not None:
                self._name = f'Crawler_{Crawler.CRAWLER_NR}/{self.flag}'
            else:
                self._name = f'Crawler_{Crawler.CRAWLER_NR}'
            Crawler.CRAWLER_NR += 1
        else:
            self._name = name
        if self.flag is None and self._name is not None:
            split_name = self._name.split('/')
            if len(split_name) > 0:
                self.flag = split_name[1]

        self.configuration = configuration
        self.agent = agent
        if schedule is None:
            self._schedule = TimeHandler(self.agent.location,
                                         interval=120,
                                         wake_time=9 * 60 * 60,
                                         bed_time=16 * 60 * 60,
                                         day_delta=day_delta)
        else:
            self._schedule = schedule
        self.queues = {}
        self.proxy = proxy
        self.active = active
        self._testing = testing
        self._crawler_info = crawler_info
        self.experiment_id = experiment_id

    @property
    def schedule(self):
        return self._schedule

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, config):
        if config is None:
            self._configuration = Config(
                name=self._name.replace('Crawler', 'Config'))
        elif type(config) is Config:
            self._configuration = config
        else:
            raise TypeError(f'configuration must be a  a  Config object')

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, agent_in):
        if agent_in is None:
            name = self._name.replace('Crawler', 'Agent')
            name = name.replace('crawler', 'agent')
            self._agent = Agent(name=name,
                                location=self._configuration.location)

        elif type(agent_in) is Agent:
            self._agent = agent_in
        else:
            raise TypeError(
                f'agents must be a list of or a single Agent object')

    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, proxy_in):
        if proxy_in is None:
            name = self._name.replace('Crawler', 'Proxy')
            name = name.replace('crawler', 'proxy')
            self._proxy = Proxy(name=name)

        elif type(proxy_in) is Proxy:
            self._proxy = proxy_in
        else:
            raise TypeError(
                f'proxies must be a list of or a single Proxy object')

    def as_dict(self):
        """
        Returns:
            - dictionary version of object, valid format for primemover_api
        """
        return_dict = {
            "name": self._name,
            "description": self._description,
            "active": self.active,
            "testing": self._testing,
            "experiment_id": self.experiment_id}
        if self._crawler_info is not None:
            for key, value in self._crawler_info.as_dict().items():
                return_dict[key] = value
            # return_dict['agent_id'] = self.agent.id
            # return_dict['configuration_id'] = self.configuration.id
            # return_dict['proxy_id'] = self.proxy.id
        else:
            return_dict["configuration"] = [self._configuration.as_dict()]
            return_dict["agent"] = [self.agent.as_dict()]
            return_dict["proxy"] = [self.proxy.as_dict()]
        return_dict["queues"] = [x.as_dict() for x in self.queues.values()]
        return return_dict

    @classmethod
    def from_list(cls, crawler_list, day_delta=0):
        """
        Initialize crawler objects from list of crawlers in dictionary format
        Arguments:
            crawler_list: list of dictionaries
            day_delta: day delta for crawler TimeHandler
                default: 0
        Returns:
            list of crawlers
        """
        crawlers = [cls._single_crawler(ind_crawler, day_delta) for
                    ind_crawler in crawler_list]
        return crawlers

    @classmethod
    def from_dict(cls, crawler_dict, day_delta=0):
        """
        Initialize crawler objects from dictionary of crawlers in dictionary format by checking
            for two plausible keys.
        Arguments:
            crawler_dict: list of dictionaries
            day_delta: day delta for crawler TimeHandler
                default: 0
        Returns:
            list of crawlers
        """
        if 'crawlers' in crawler_dict.keys():
            crawlers = [cls._single_crawler(ind_crawler, day_delta) for
                        ind_crawler in crawler_dict['crawlers']]
        elif 'data' in crawler_dict.keys():
            crawlers = [cls._single_crawler(ind_crawler, day_delta) for
                        ind_crawler in crawler_dict['data']]
        else:
            crawlers = [cls._single_crawler(crawler_dict, day_delta)]
        return crawlers

    @classmethod
    def _single_crawler(cls, crawler_dict, day_delta=0):
        crawler_object = cls(name=crawler_dict.get('name'),
                             description=crawler_dict.get('description'),
                             configuration=Config.from_dict(
                                 crawler_dict.get('configuration')),
                             agent=Agent.from_dict(crawler_dict.get('agent')),
                             proxy=Proxy.from_dict(crawler_dict.get('proxy')),
                             crawler_info=CrawlerInfo.from_dict(crawler_dict),
                             experiment_id=crawler_dict.get('experiment_id'),
                             day_delta=day_delta
                             )

        return crawler_object

    def add_task(self, cls, to_session=None, params=None, start_at=None):
        """
        Add a new task to the crawler
        Arguments:
            - cls: class of the desired task, subclass of Queue (see. Tasks.py for available tasks)
            - to_session: session_id (int) to add to existing queue if the session_id exists. Else a new queue is generated.
            - params: dictionary, required parameters for the defined class (required, if and when class requires parameters)
            - start_at: start_time, default: generated by self._schedule
        Returns:
            session_id
        """
        if not issubclass(cls, Tasks.Queue):
            raise TypeError(f'cls must be a subclass of Queue')
        # generate new object
        if start_at is None and to_session is None or to_session is False:
            start_at = self._schedule.new_time()
        if cls.PASS_CRAWLER:
            if params is not None:
                new_queue_object = cls(crawler=self, start_at=start_at,
                                       **params)
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
                self.queues[to_session] = Tasks.Queue(start_at=start_at,
                                                      name=f'Session_{to_session}',
                                                      delay_min=1,
                                                      delay_max=10)
            self.queues[to_session] + new_queue_object
        # add to queue list as new session
        else:
            to_session = Util.new_key(self.queues)
            self.queues[to_session] = new_queue_object
        return to_session

    def add_tasks(self, cls, nr: int, to_session, params=None, consecutive=False,
                  time_list=None):
        """
        Arguments:
            - cls: class of the desired task, subclass of Queue (see. Tasks.py for available tasks)
            - nr: number of times this task is to be added
            - to_session: session_id (int) to add to existing queue if the session_id exists. Else a new queue is generated.
            - params: dictionary, required parameters for the defined class (required, if and when class requires parameters)
                Note, all tasks generated here will recive the same set of parameters
            - consecutive: boolean, if True, tasks are scheduled consecutivley, even if not in a single session
            - time_list: list of start times
        Returns:
            session_id
        """
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
                    to_session = self.add_task(cls, params=params, start_at=t)
            else:
                for i in range(nr):
                    to_session = self.add_task(cls, params=params)
        else:
            for i in range(nr):
                to_session = self.add_task(cls, to_session=to_session,
                                           params=params)
        return to_session

    def clear_day(self):
        self.queues = {}
