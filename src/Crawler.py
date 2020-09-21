from src.ConfigureProfile import *
from src.Info import Agent, Proxy
from src.TimeHandler import TimeHandler
from src.Preferences import *
from src.Tasks import *


class Crawler:
    CRAWLER_NR = 0

    def __init__(self,
                 global_schedule=None,
                 name=None,
                 description="Crawler created through py",
                 configuration=None,
                 agent=None,
                 proxy=None, active=1, schedule=None, testing=0):
        self._description = description
        if name is None:
            self._name = f'Crawler_{Crawler.CRAWLER_NR}'
            Crawler.CRAWLER_NR += 1
        else:
            self._name = name
        self.configuration = configuration
        self.agent = agent
        if schedule is None and global_schedule is not None:
            self._schedule = TimeHandler(global_schedule,
                                         self.agent[0].location,
                                         interval=120,
                                         bed_time=19 * 60 * 60,
                                         wake_time=17.75 * 60 * 60)
        elif schedule is None and global_schedule is None:
            raise Exception('f global_schedule and schedule cant bot be None')
        else:
            self._schedule = schedule
        self.queues = []
        self.proxy = proxy
        self.active = active
        self._testing = testing

    @property
    def schedule(self):
        return self._schedule

    @property
    def configuration(self):
        return self._configurations

    @configuration.setter
    def configuration(self, configs):
        if configs is None:
            self._configurations = [Config()]
        elif type(configs) is list:
            check_types = [type(val) is Config for val in configs]
            if False in check_types:
                raise TypeError(
                    'All entries in configurations must be of type Config')
            else:
                self._configurations = configs
        elif type(configs) is Config:
            self._configurations = [configs]
        else:
            raise TypeError(

                f'configurations must be a list of or a single Config object')

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

    def __str__(self):
        crawler_descr = \
            f'"name": "{self._name or ""}",\n' \
            f'"description": "{self._description or ""}",\n'
        formatted = ",\n".join([str(x) for x in self.queues])
        return f'{{{crawler_descr},"queues": [\n{formatted}]}}'

    def as_dict(self):
        return {
            "name": self._name,
            "description": self._description,
            "active": self.active,
            "testing": self._testing,
            "configuration": [x.as_dict() for x in self.configuration],
            "agent": [x.as_dict() for x in self.agent],
            "proxy": [x.as_dict() for x in self.proxy],
            "queues": [x.as_dict() for x in self.queues]}

    def add_searches(self, nr, t_list=None):
        terms = self.configuration[0].terms
        to_search = random.choices(terms, k=nr)
        if t_list is None:
            for term in to_search:
                self.queues.append(
                    GoogleSearch(term, self.schedule.new_time()))
        else:
            for term, t in zip(to_search, t_list):
                self.queues.append(
                    GoogleSearch(term, t))

    def add_direct_visits(self, nr, t_list=None):
        outlets = self.configuration[0].media
        to_visit = random.choices(outlets, k=nr)
        if t_list is None:
            for outlet in to_visit:
                self.queues.append(
                    VisitDirect(outlet, self.schedule.new_time()))
        else:
            for outlet, t in zip(to_visit, t_list):
                self.queues.append(
                    VisitDirect(outlet, t))
