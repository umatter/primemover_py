import src.worker.Jobs as Jobs
import random as r


class Queue:
    PASS_CRAWLER = False
    def __init__(self,
                 start_at,
                 name="",
                 description="A single browser session",
                 delay_min=0,
                 delay_max=10,
                 ):
        self._description = description
        self._name = name
        self._start_at = start_at
        self.jobs = []
        self.delay_min = min(delay_min, delay_min)
        self.delay_max = max(delay_max, delay_min)

    @property
    def start_at(self):
        return self._start_at

    @property
    def delay_min(self):
        return self._delay_min

    @delay_min.setter
    def delay_min(self, val):
        if type(val) is int:
            self._delay_min = val
        elif type(val) is float:
            self._delay_min = int(val)
        else:
            raise TypeError('delay_min should be type int')

    @property
    def delay_max(self):
        return self._delay_max

    @delay_max.setter
    def delay_max(self, val):
        if type(val) is int:
            self._delay_max = val
        elif type(val) is float:
            self._delay_max = int(val)
        else:
            raise TypeError('delay_min should be type int')

    def __str__(self):
        queue_descr = \
            f'"name": "{self._name}",\n' \
            f'"description": "{self._description}",\n' \
            f'"start_at": "{self._start_at}"'
        formatted = ",\n".join([str(x) for x in self.jobs])
        return f'{{{queue_descr},"jobs": [\n{formatted}]}}'

    def as_dict(self):
        return {
            "name": self._name,
            "description": self._description,
            "start_at": self._start_at,
            "jobs": [x.as_dict() for x in self.jobs]}

    def __add__(self, other):
        delay = r.randint(self.delay_min, self.delay_max)
        self.jobs.append(Jobs.Wait(delay))
        self.jobs = self.jobs + other.jobs
