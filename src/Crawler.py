from src.ConfigureProfile import *
from src.Info import Agent, Proxy, CrawlerInfo
from src.TimeHandler import TimeHandler
from src.Preferences import *
from src.Tasks import *
import src.Utilities as Util


class Crawler:
    CRAWLER_NR = 0

    def __init__(self,
                 global_schedule=None,
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
        if schedule is None and global_schedule is not None:
            self._schedule = TimeHandler(global_schedule,
                                         self.agent[0].location,
                                         interval=120,
                                         bed_time=9 * 60 * 60,
                                         wake_time=7 * 60 * 60,
                                         tomorrow=False)
        elif schedule is None and global_schedule is None:
            raise Exception('f global_schedule and schedule cant bot be None')
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
        return_dict = {
            "name": self._name,
            "description": self._description,
            "active": self.active,
            "testing": self._testing,
            "configuration": [x.as_dict() for x in self.configuration],
            "agent": [x.as_dict() for x in self.agent],
            "proxy": [x.as_dict() for x in self.proxy],
            "queues": [x.as_dict() for x in self.queues.values()]}
        if self._crawler_info is not None:
            for key, value in self._crawler_info.as_dict().items():
                return_dict['key'] = value
        return return_dict

    def add_searches(self, terms=None, nr=1, t_list=None, to_session=None):
        if terms is None:
            terms = self.configuration[0].terms
            to_search = random.choices(terms, k=nr)
        elif type(terms) is list and len(terms) == nr:
            to_search = terms
        elif type(terms) is list:
            raise ValueError(
                f'There is a strange number of search terms in the passed list')
        elif type(terms) is str:
            to_search = [terms for i in range(nr)]
        else:
            raise TypeError(
                f'terms must be a single string, None or a list of strings')

        if t_list is None and to_session is None:
            t_list = self.schedule.consecutive_times(nr)
        if to_session is None:
            for term, t in zip(to_search, t_list):
                self.queues[Util.new_key(self.queues)] = (GoogleSearch(term, t))
        else:
            if t_list is None and to_session not in self.queues.keys():
                t = self.schedule.new_time()
            elif to_session in self.queues.keys():
                t = self.queues[to_session].start_at
            elif type(t_list) is list:
                t = t_list[0]
            else:
                t = t_list

            if to_session not in self.queues.keys():
                to_session = Util.new_key(self.queues)
                self.queues[to_session] = Queue(start_at=t,
                                                name=f'Session_{to_session}',
                                                delay_min=1,
                                                delay_max=10)

            for term in to_search:
                self.queues[to_session] + GoogleSearch(term, t)

            return to_session

    def add_direct_visits(self, outlets=None, nr=1, t_list=None,
                          to_session=None):
        if outlets is None:
            outlets = self.configuration[0].media
            to_visit = random.choices(outlets, k=nr)
        elif type(outlets) is list and len(outlets) == nr:
            to_visit = outlets
        elif type(outlets) is list:
            raise ValueError(
                f'There is a strange number of outlets in the passed list')
        elif type(outlets) is str:
            to_visit = [outlets for i in range(nr)]
        else:
            raise TypeError(
                f'outlets must be a single string, None or a list of strings')

        if t_list is None and to_session is None:
            t_list = self.schedule.consecutive_times(nr)
        if to_session is None:
            for outlet, t in zip(to_visit, t_list):
                self.queues[len(self.queues)] = (VisitDirect(outlet, t))
        else:
            if t_list is None and to_session not in self.queues.keys():
                t = self.schedule.new_time()
            elif to_session in self.queues.keys():
                t = self.queues[to_session].start_at
            elif type(t_list) is list:
                t = t_list[0]
            else:
                t = t_list

            if to_session not in self.queues.keys():
                to_session = Util.new_key(self.queues)
                self.queues[to_session] = Queue(start_at=t,
                                                name=f'Session_{to_session}',
                                                delay_min=1,
                                                delay_max=10)
            for outlet in to_visit:
                self.queues[to_session] + VisitDirect(outlet, t)
            return to_session

    @classmethod
    def from_dict(cls, crawler_dict, global_schedule):
        if 'crawlers' in crawler_dict.keys():
            crawlers = [cls._single_crawler(ind_crawler, global_schedule) for
                        ind_crawler in crawler_dict['crawlers']]
        else:
            crawlers = [cls._single_crawler(crawler_dict, global_schedule)]
        return crawlers

    @classmethod
    def _single_crawler(cls, crawler_dict, global_schedule):
        proxy_object = cls(name=crawler_dict.get('name'),
                           description=crawler_dict.get('description'),
                           global_schedule=global_schedule,
                           configuration=Config.from_dict(crawler_dict['configuration']),
                           agent=Agent.from_dict(crawler_dict.get('agent')),
                           proxy=Proxy.from_dict(crawler_dict.get('proxy')),
                           crawler_info=CrawlerInfo.from_dict(crawler_dict)
                           )

        return proxy_object

if __name__ == "__main__":
    import json
    from src.TimeHandler import Schedule
    with open('resources/examples/example_output.json', 'r') as in_file:
        data = json.load(in_file)
    trial_crawlers = Crawler.from_dict(data, Schedule())
    print(trial_crawlers)
