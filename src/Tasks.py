import src.Jobs as Jobs
from src.Info import *
import random as r


class Queue:
    def __init__(self,
                 queue_info,
                 start_at,
                 name="",
                 description="",
                 ):
        self.queue_info = queue_info
        self._description = description
        self._name = name
        self._start_at = start_at
        self.jobs = []

    @property
    def queue_info(self):
        return self._queue_info

    @queue_info.setter
    def queue_info(self, info):
        if not type(info) is QueueInfo:
            raise TypeError('queue_info must be of type QueueInfo')
        else:
            self._queue_info = info

    def __str__(self):
        queue_descr = \
            f'"id": {self.queue_info.queue_id},\n' \
            f'"user_id": "{self.queue_info._user_id}",\n' \
            f'"queue_id": {self.queue_info.queue_id},\n' \
            f'"name": "{self._name}",\n' \
            f'"description": "{self._description}",\n' \
            f'"started": {self.queue_info.started},\n' \
            f'"success": {self.queue_info.success},' \
            f' "failure": {self.queue_info.failure},' \
            f'"order": {self.queue_info.order},\n' \
            f'"active": {self.queue_info.active},\n' \
            f'"start_at": "{self._start_at}"'

        formatted = ",\n".join([str(x) for x in self.jobs])
        return f'{{{queue_descr},"jobs": [\n{formatted}]}}'


class GoogleSearch(Queue):
    """
    Conduct a google search and scroll to the bottom of the page
    """

    def __init__(self, term, start_time, queue_info):
        self._search_term = term
        super().__init__(queue_info=queue_info,
                         start_at=start_time,
                         name='GoogleSearch',
                         description='Open Google, enter a search querry and select a result.')
        # Add Job to Visit a webpage (google)
        self.jobs.append(Jobs.VisitJob(job_info=queue_info.new_job(),
                                       url='https://www.google.com'))

        # Add Job to select the search field via XPATH and type the search term
        self.jobs.append(Jobs.EnterText(job_info=queue_info.new_job(),
                                        text=term,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH')
                         )
        # Add Job to select a result randomly
        self.jobs.append(Jobs.SingleSelect(job_info=queue_info.new_job(),
                                           selector="LC20lb.DKV0Md",
                                           selector_type='CLASS',
                                           decision_type="RANDOM"
                                           )
                         )

        # Add Job to scroll down 80% of the visited page
        self.jobs.append(Jobs.Scroll(job_info=queue_info.new_job(),
                                     direction='DOWN',
                                     percentage=80))


class VisitDirect(Queue):
    """
        Visit a media outlet and scroll for 2-3 minutes
    """

    def __init__(self, outlet_url, start_time, queue_info):
        self._outlet_url = outlet_url
        self._duration = 60 * r.uniform(2, 3)  # choose scroll time in seconds
        super().__init__(queue_info=queue_info,
                         start_at=start_time,
                         name='Visit Direct',
                         description='Visit a media outlet and scroll for 2-3 minutes.')
        # Add Job to Visit a media outlet
        self.jobs.append(Jobs.VisitJob(job_info=queue_info.new_job(),
                                       url=self._outlet_url))

        # Add Job to scroll down for random time between 2 and 3 minutes
        self.jobs.append(Jobs.Scroll(job_info=queue_info.new_job(),
                                     direction='DOWN',
                                     duration=self._duration))


class VisitViaGoogle(Queue):
    """
        Visit a media outlet and scroll for 2-3 minutes
    """

    def __init__(self, outlet_name, start_time, queue_info):
        self._outlet_name = outlet_name
        self._duration = 60 * r.uniform(2, 3)  # choose scroll time in seconds
        super().__init__(queue_info=queue_info,
                         start_at=start_time,
                         name='Visit via Googe',
                         description='Visit a media outlet via google and scroll for some time.')
        # Add Job to Visit a  Google
        self.jobs.append(Jobs.VisitJob(job_info=queue_info.new_job(),
                                       url='https://www.google.com'))

        # Add Job to select the search field via XPATH and type the outlets name
        self.jobs.append(Jobs.EnterText(job_info=queue_info.new_job(),
                                        text=self._outlet_name,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH')
                         )
        # Add Job to wait for a random nr. of seconds
        self.jobs.append(Jobs.Wait(job_info=queue_info.new_job(),
                                   time=r.uniform(1,6)
                                   )
                         )

        # Add Job to select the first result
        self.jobs.append(Jobs.SingleSelect(job_info=queue_info.new_job(),
                                           selector="LC20lb.DKV0Md",
                                           selector_type='CLASS',
                                           decision_type="FIRST"
                                           )
                         )

        # Add Job to scroll down the visited page for some time
        self.jobs.append(Jobs.Scroll(job_info=queue_info.new_job(),
                                     direction='DOWN',
                                     duration=self._duration))

