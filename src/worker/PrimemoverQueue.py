"""Queue.py defines the base Queue class. This class mirrors the queue object in the API
and represents a single browser session. It contains all the jobs that are to be conducted in such a
session and when to begin execution. Queues can be combined

J.L. 11.2020
"""

import src.worker.jobs as jobs
import random as r


class Queue:
    """Base queue class
    Public Arguments:
        - description: string
        - name: string
        - start_at: string, ISO format
        - jobs: list of job objects
        - delay_min: int, min wait time between appended queues in seconds
        - delay_max: int, max wait time between appended queues in seconds
    """
    PASS_CRAWLER = False

    def __init__(self,
                 start_at,
                 name="",
                 description="A single browser session",
                 delay_min=1,
                 delay_max=10,
                 ):
        self.description = description
        self.name = name
        self.start_at = start_at
        self.jobs = []
        self.delay_min = min(delay_min, delay_min)
        self.delay_max = max(delay_max, delay_min)

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
            f'"name": "{self.name}",\n' \
            f'"description": "{self.description}",\n' \
            f'"start_at": "{self.start_at}"'
        formatted = ",\n".join([str(x) for x in self.jobs])
        return f'{{{queue_descr},"jobs": [\n{formatted}]}}'

    def as_dict(self):
        """Create valid dictionary version of queue
        Returns: dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "start_at": self.start_at,
            "jobs": [x.as_dict() for x in self.jobs]}

    def __add__(self, other):
        """
        Combine two queues into one (queue_a + queue_b)
        other: second queue object
        """
        delay = r.randint(self.delay_min, self.delay_max)
        self.jobs.append(jobs.Wait(delay))
        self.jobs = self.jobs + other.jobs
        return self
