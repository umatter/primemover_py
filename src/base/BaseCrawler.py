"""
This module contains the Crawler class. The crawler class can be used to combine
configurations, proxy and agent information and schedule new tasks, potentially
based on this information. This can then be exported and pushed to the primemover_api

J.L. 11.2020
"""

from src.base.BaseConfig import BaseConfig
from src.worker.info import CrawlerInfo
from src.base.BaseAgent import BaseAgent
from src.base.BaseProxy import BaseProxy
from src.worker.TimeHandler import TimeHandler
import src.worker.utilities as util
from src.worker.PrimemoverQueue import Queue
from datetime import datetime


class BaseCrawler:
    """ Crawler combines all relevant information about an individual bot. It contains
    configuration, proxy, agent, queue (task) data and the necessary information
    to re-identify a crawler both in the primemover_api and in primemover_py.

    Public arguments:
        - name: string, optional but recomended, can be used to store information for processing
            passing  <<some_name>>/<<flag>> will set the flag parameter if none is set.
        - description: string, optional
        - configuration: a configuration object.
            default: generates a new config object with all parameters determined
            through CONFIGURATION_FUNCTIONS or defaults. The name defaults to a modified version of the crawler name.
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
    CONFIG_CLASS = BaseConfig
    AGENT_CLASS = BaseAgent
    PROXY_CLASS = BaseProxy

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
                 date_time=datetime.now()
                 ):
        self.flag = flag
        self._description = description
        self.name = name
        if self.flag is None and self._name is not None:
            split_name = self._name.split('/')
            if len(split_name) > 1:
                self.flag = split_name[1]
        self.configuration = configuration
        self.send_agent = False
        self.agent = agent
        self._date_time = date_time
        self.schedule = schedule
        self.queues = {}
        self.proxy = proxy
        self.active = active
        self._testing = testing
        self._crawler_info = crawler_info
        self.experiment_id = experiment_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        if val is None:
            if self.flag is not None:
                self._name = f'Crawler_{BaseCrawler.CRAWLER_NR}/{self.flag}'
            else:
                self._name = f'Crawler_{BaseCrawler.CRAWLER_NR}'
            BaseCrawler.CRAWLER_NR += 1
        else:
            self._name = val

    @property
    def send_agent(self):
        return self._send_agent

    @send_agent.setter
    def send_agent(self, val=False):
        if type(val) is bool:
            self._send_agent = val
        else:
            raise TypeError('expected boolean send agent')

    @property
    def schedule(self):
        return self._schedule

    @schedule.setter
    def schedule(self, val):
        if val is None:
            self._schedule = TimeHandler(self.agent.location,
                                         interval=120,
                                         wake_time=10 * 60 * 60,
                                         bed_time=17 * 60 * 60,
                                         date_time=self._date_time)
        else:
            self._schedule = val

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, config):
        if config is None:
            self._configuration = self.CONFIG_CLASS(
                name=self._name.replace('Crawler', 'CONFIGURATION_FUNCTIONS'))
        elif type(config) is self.CONFIG_CLASS:
            self._configuration = config
        else:
            raise TypeError(
                f'configuration must be a  a  CONFIGURATION_FUNCTIONS object')

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, agent_in):
        if agent_in is None:
            self.send_agent = True
            name = self._name.replace('Crawler', 'Agent')
            name = name.replace('crawler', 'agent')
            self._agent = self.AGENT_CLASS(name=name,
                                           location=self._configuration.location)

        elif type(agent_in) is self.AGENT_CLASS:
            self.send_agent = False
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
            self._proxy = self.PROXY_CLASS(name=name)

        elif type(proxy_in) is self.PROXY_CLASS:
            self._proxy = proxy_in
        else:
            raise TypeError(
                f'proxies must be a list of or a single Proxy object')

    @property
    def crawler_info(self):
        return self._crawler_info

    def as_dict(self, object_ids=False):
        """
        Returns:
            - dictionary version of object, valid format for primemover_api
        """
        return_dict = {
            "name": self._name,
            "description": self._description,
            "active": self.active,
            "testing": self._testing,
            "configuration": [self.configuration.as_dict()],
            "proxy": [self.proxy.as_dict()],
        }
        if self.experiment_id is not None:
            return_dict["experiment_id"] = self.experiment_id
        if self.send_agent:
            return_dict["agent"] = [self.agent.as_dict()]
        if self._crawler_info is not None:
            return_dict['id'] = self._crawler_info.crawler_id
        if object_ids:
            return_dict['agent_id'] = self.agent.info.agent_id
            return_dict[
                'configuration_id'] = self.configuration.info.configuration_id
            # return_dict['proxy_id'] = self.proxy._info.proxy_id

        return_dict["queues"] = [x.as_dict() for x in self.queues.values()]

        return return_dict

    def add_task(self, cls, to_session=None, params=None, start_at=None):
        """
        Add a new task to the crawler
        Arguments:
            - cls: class of the desired task, subclass of Queue (see. Tasks.py for available tasks)
            - to_session: session_id (int) to add to existing queue if the session_id exists. Else a new queue is generated.
            - params: dictionary, required parameters for the defined class (required, if and when class requires parameters)
            - start_at: start_time, default: generated by self.schedule
        Returns:
            session_id
        """
        if not issubclass(cls, Queue):
            raise TypeError(f'cls must be a subclass of Queue')
        # generate new object
        if start_at is None and to_session is None or to_session is False:
            start_at = self.schedule.new_time()
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
                    start_at = self.schedule.new_time()
                to_session = util.new_key(self.queues)
                self.queues[to_session] = Queue(start_at=start_at,
                                                name=f'Session_{to_session}',
                                                delay_min=1,
                                                delay_max=10)
            self.queues[to_session] + new_queue_object
        # add to queue list as new session
        else:
            to_session = util.new_key(self.queues)
            self.queues[to_session] = new_queue_object
        return to_session

    def add_tasks(self, cls, nr: int, to_session, params=None,
                  consecutive=False,
                  time_list=None):
        """
        Arguments:
            - cls: class of the desired task, subclass of Queue (see. task files for available tasks)
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
            time_list = self.schedule.consecutive_times(nr)

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

    @classmethod
    def from_list(cls, crawler_list, date_time=datetime.now()):
        """
        Initialize crawler objects from list of crawlers in dictionary format
        Arguments:
            crawler_list: list of dictionaries
            date_time: day datetime for crawler TimeHandler
                default: current datetime
        Returns:
            list of crawlers
        """

        crawlers = [cls._single_crawler(ind_crawler, date_time) for
                    ind_crawler in crawler_list]
        return crawlers

    @classmethod
    def from_dict(cls, crawler_dict: dict, date_time=datetime.now()):
        """
        Initialize crawler objects from dictionary of crawlers in dictionary format by checking
            for two plausible keys.
        Arguments:
            crawler_dict: list of dictionaries
            date_time: day datetime for crawler TimeHandler
                default: current datetime
        Returns:
            list of crawlers
        """
        if 'crawlers' in crawler_dict.keys():
            crawlers = [cls._single_crawler(ind_crawler, date_time) for
                        ind_crawler in crawler_dict['crawlers']]
        elif 'data' in crawler_dict.keys():
            crawlers = [cls._single_crawler(ind_crawler, date_time) for
                        ind_crawler in crawler_dict['data']]
        else:
            crawlers = [cls._single_crawler(crawler_dict, date_time)]
        return crawlers

    @classmethod
    def _single_crawler(cls, crawler_dict, date_time):
        agent = cls.AGENT_CLASS.from_dict(crawler_dict.get('agent'))
        crawler_object = cls(name=crawler_dict.get('name'),
                             description=crawler_dict.get('description'),
                             configuration=cls.CONFIG_CLASS.from_dict(
                                 crawler_dict.get('configuration'),
                                 location=agent.location, date_time=date_time),
                             agent=agent,
                             proxy=cls.PROXY_CLASS.from_dict(
                                 crawler_dict.get('proxy')),
                             crawler_info=CrawlerInfo.from_dict(crawler_dict),
                             experiment_id=crawler_dict.get('experiment_id'),
                             date_time=date_time
                             )
        crawler_object.send_agent = False
        return crawler_object

    def clear_day(self):
        self.queues = []

    def update_crawler(self, results=None, proxy_update=None, terms=True):
        update_location = None
        if proxy_update is not None:
            update_location = self.proxy.update_proxy(proxy_update)
            if update_location == 'not updated':
                update_location = None

        if update_location is not None:
            self.agent.location = update_location
            self.send_agent = True
        results_valid = []
        if results is not None:
            relevant_results = results.get(str(self._crawler_info.crawler_id),
                                           'skip')
            if relevant_results == 'skip':
                return self
            results_selected = [result.get('data') for result in
                                relevant_results]

            results_selected = list(filter(None, results_selected))
            for res in results_selected:
                if res.get('pi') is not None:
                    results_valid.append(res)

        self.configuration.update_config(results_valid, update_location,
                                         terms=terms)

        return self
