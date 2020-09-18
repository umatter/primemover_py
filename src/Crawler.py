from src.ConfigureProfile import *
from src.Info import Agent, Proxy
from src.TimeHandler import TimeHandler
from src.Preferences import *
from src.Tasks import *


class Crawler:
    def __init__(self, global_schedule=None, name="Just a crawler",
                 description="Crawler created through py", configurations=None,
                 agents=None, proxies=None, active=0, schedule=None):
        self._description = description
        self._name = name
        self.configurations = configurations
        self.agents = agents
        if schedule is None and global_schedule is not None:
            self._schedule = TimeHandler(global_schedule,
                                         self.agents[0].location,
                                         interval=120,
                                         bed_time=14.5 * 60 * 60,
                                         wake_time=12 * 60 * 60)
        elif schedule is None and global_schedule is None:
            raise Exception('f global_schedule and schedule cant bot be None')
        else:
            self._schedule = schedule
        self.queues = []
        self.proxies = proxies
        self.active = active

    @property
    def schedule(self):
        return self._schedule

    @property
    def configurations(self):
        return self._configurations

    @configurations.setter
    def configurations(self, configs):
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
    def agents(self):
        return self._agents

    @agents.setter
    def agents(self, agents_in):
        if agents_in is None:
            self._agents = [Agent()]
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
    def proxies(self):
        return self._proxies

    @proxies.setter
    def proxies(self, proxies_in):
        if proxies_in is None:
            self._proxies = []
        elif type(proxies_in) is list:
            check_types = [type(val) is Proxy for val in proxies_in]
            if False in check_types:
                raise TypeError(
                    'All entries in proxies must be of type Proxy')
            else:
                self._proxies = proxies_in
        elif type(proxies_in) is Proxy:
            self._proxies = [proxies_in]
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
            "configurations": [x.as_dict() for x in self.configurations],
            "agents": [x.as_dict() for x in self.agents],
            "proxies": [x.as_dict() for x in self.proxies],
            "queues": [x.as_dict() for x in self.queues]}

    def add_searches(self, nr, t_list=None):
        terms = self.configurations[0].terms
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
        outlets = self.configurations[0].media
        to_visit = random.choices(outlets, k=nr)
        if t_list is None:
            for outlet in to_visit:
                self.queues.append(
                    VisitDirect(outlet, self.schedule.new_time()))
        else:
            for outlet, t in zip(to_visit, t_list):
                self.queues.append(
                    VisitDirect(outlet, t))
