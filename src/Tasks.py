import src.Jobs as Jobs
import random as r


class Queue:
    def __init__(self,
                 start_at,
                 name="",
                 description="",
                 ):
        self._description = description
        self._name = name
        self._start_at = start_at
        self.jobs = []

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


class GoogleSearch(Queue):
    """
    Conduct a google search and scroll to the bottom of the page
    """

    def __init__(self, term, start_time):
        self._search_term = term
        super().__init__(start_at=start_time,
                         name='GoogleSearch',
                         description='Open Google, enter a search querry and select a result.')
        # Add Job to Visit a webpage (google)
        self.jobs.append(Jobs.VisitJob(url='https://www.google.com'))

        # Add Job to select the search field via XPATH and type the search term
        self.jobs.append(Jobs.EnterText(text=term,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS")
                         )
        # Add Job to select a result randomly
        self.jobs.append(Jobs.SingleSelect(selector="LC20lb.DKV0Md",
                                           selector_type='CLASS',
                                           decision_type="RANDOM"
                                           )
                         )

        # Add Job to scroll down 80% of the visited page
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     percentage=80))


class VisitDirect(Queue):
    """
        Visit a media outlet and scroll for 2-3 minutes
    """

    def __init__(self, outlet_url, start_time):
        self._outlet_url = outlet_url
        self._duration = r.randint(60, 180)  # choose scroll time in seconds
        super().__init__(start_at=start_time,
                         name='Visit Direct',
                         description='Visit a media outlet and scroll for 2-3 minutes.')
        # Add Job to Visit a media outlet
        self.jobs.append(Jobs.VisitJob(url=self._outlet_url))

        # Add Job to scroll down for random time between 1 and 3 minutes
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=self._duration))


class VisitViaGoogle(Queue):
    """
        Visit a media outlet and scroll for 2-3 minutes
    """

    def __init__(self, outlet_name, start_time):
        self._outlet_name = outlet_name
        self._duration = r.randint(60, 180)  # choose scroll time in seconds
        super().__init__(start_at=start_time,
                         name='Visit via Googe',
                         description='Visit a media outlet via google and scroll for some time.')
        # Add Job to Visit a  Google
        self.jobs.append(Jobs.VisitJob(url='https://www.google.com'))

        # Add Job to select the search field via XPATH and type the outlets name
        self.jobs.append(Jobs.EnterText(text=self._outlet_name,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH')
                         )
        # Add Job to wait for a random nr. of seconds
        self.jobs.append(Jobs.Wait(time=r.randint(1, 6)
                                   )
                         )

        # Add Job to select the first result
        self.jobs.append(Jobs.SingleSelect(selector="LC20lb.DKV0Md",
                                           selector_type='CLASS',
                                           decision_type="FIRST"
                                           )
                         )

        # Add Job to scroll down the visited page for some time
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=self._duration))
