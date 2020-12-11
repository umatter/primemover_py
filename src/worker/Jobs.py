"""
Jobs.py creates the base job class and a series of 'Jobs'. These are jobs as they
can be run by the primemover_runner. Variables that the runner needs to execute and
recognize these jobs are passed as 'behaviors', which are defined in Behavior.py.
These behaviors parse input for validity.

Classes:
    - Job: base job class
"""

import src.worker.Behavior as Behavior

class Job:
    """
    Base class
    Public Arguments:
        - job_type: string, required field indicating type of job. Must be recognized by runner
        - name: string
        - description: string
        - behaviors: list of behavior objects
    """

    def __init__(self,
                 job_type,
                 name="",
                 description="",
                 task=None,
                 flag=None,
                 ):
        self.type = job_type
        self._description = description
        self._name = name
        self.behaviors = []
        if task is not None:
            self.behaviors.append(Behavior.TaskBehavior(task))
        if flag is not None:
            self.behaviors.append(Behavior.FlagBehavior(flag))

    def as_dict(self):
        """
        Convert to API compatible dict
        Returns: dictionary
        """
        return {
            "name": self._name,
            "type": self.type,
            "description": self._description,
            "behaviors": [x.as_dict() for x in self.behaviors]}


class VisitJob(Job):
    """
    Visit a URL
    """

    def __init__(self, url,
                 task=None,
                 flag=None):
        """
        Arguments:
            - url: A valid URL to visit
            - task: (optional) string,  task the job is a part of
            - flag: (optional) string,  some flag
        """
        super().__init__(job_type='visitjob', name='Visit',
                         description=f'Visit {url}', task=task, flag=flag)
        self.behaviors.append(Behavior.URL(url))


class Wait(Job):
    """Wait for a predetermine number of seconds"""

    def __init__(self, time,
                 task=None,
                 flag=None):
        """
        Arguments:
            - time: Wait time in seconds
            - task: (optional) string,  task the job is a part of
            - flag: (optional) string,  some flag
        """
        super().__init__(job_type='waitjob', name='Wait',
                         description=f'Wait for {time} seconds', task=task,
                         flag=flag)
        self.behaviors.append(
            Behavior.WaitSeconds(time))


class EnterText(Job):
    """Enter text into some field"""

    def __init__(self,
                 text,
                 selector,
                 selector_type='XPATH',
                 send_return=True,
                 type_mode="SIMULATED_NOTYPOS",
                 task=None,
                 flag=None
                 ):
        """
            - text: string, text to enter
            - selector: string, a valid XPATH|CSS|CLASS|ID for a text field, default: 'XPATH'
            - send_return: Boolean, if True, the return key is hit upon completion of typing, default:'True'
            - type_mode: Method of text entry.  str, in {"DIRECT","SIMULATED_KEEPINGTYPOS","SIMULATED_FIXINGTYPOS","SIMULATED_NOTYPOS"}
                    Direct: send keys at once (imagine copy and paste)
                    Simulated_KeepingTypos: Simulate key presses, make typos and keep some of them
                    Simulated_FixingTypos: Simulate key presses, make typos fix all of them
                    Simulated_NoTypos: Simulate key presses, make no mistakes  (default argument)
            - selector_type: One of "XPATH|CSS|CLASS|ID"
            - task: (optional) string,  task the job is a part of
            - flag: (optional) string,  some flag
        """
        super().__init__(job_type='entertextfieldjob',
                         name='Enter Text',
                         description=f'Enter text into the defined field',
                         task=task, flag=flag)
        self.behaviors.append(Behavior.Text(text))
        self.behaviors.append(
            Behavior.SelectionType(selector_type))
        self.behaviors.append(
            Behavior.Selector(selector))
        self.behaviors.append(
            Behavior.AppendReturn(send_return))
        self.behaviors.append(
            Behavior.TypingMode(type_mode))


class SingleSelect(Job):
    """Click on an element of a website"""

    def __init__(self, selector, selector_type='XPATH',
                 decision_type='FIRST',
                 task=None,
                 flag=None):
        """
            - selector: string, a valid XPATH|CSS|CLASS|ID for a text field, default: 'XPATH'
            - selector_type: One of "XPATH|CSS|CLASS|ID"
            - decision_type: one of "FIRST|LAST|RANDOM", Method of selecting a result if multiple elements match selector (default: First)
            - task: (optional) string,  task the job is a part of
            - flag: (optional) string,  some flag
        """
        super().__init__(job_type='singleselecturljob',
                         name='Select',
                         description=f'Select an item and click', task=task,
                         flag=flag)
        self.behaviors.append(
            Behavior.SelectionType(selector_type))
        self.behaviors.append(
            Behavior.Selector(selector))
        self.behaviors.append(
            Behavior.DecisionType(decision_type))


class TryClick(Job):
    """
    click some element (differs from select, as no choices are made)
    """

    def __init__(self, selector, selector_type='XPATH',
                 task=None,
                 flag=None):
        """
            - selector: string, a valid XPATH|CSS|CLASS|ID for a text field, default: 'XPATH'
            - selector_type: One of "XPATH|CSS|CLASS|ID"
            - task: (optional) string,  task the job is a part of
            - flag: (optional) string,  some flag
        """
        super().__init__(job_type='tryclickjob',
                         name='Try Click',
                         description=f'Try to click a button/item', task=task,
                         flag=flag)
        self.behaviors.append(
            Behavior.SelectionType(selector_type))
        self.behaviors.append(
            Behavior.Selector(selector))


class Scroll(Job):
    """Scroll in some direction for a percentage of a page or a pre-determined time"""
    def __init__(self, direction='DOWN', duration=None,
                 percentage=None,
                 task=None,
                 flag=None):
        """
        Arguments:
            - direction: string,  one of "UP/U|DOWN/D" (not case sensitive)
            - duration: int, seconds>0
            - percentage: numeric in [0,100] (overwrites duration)
            """
        if percentage is not None:
            method = 'length'
        elif duration is not None:
            method = 'duration'
        else:
            raise ValueError('One of duration and length must be set')

        super().__init__(job_type=f'scrollby{method}job',
                         name=f'Scroll by {method}',
                         description=f'Scroll {direction.lower()}', task=task,
                         flag=flag)
        if method == 'length':
            self.behaviors.append(
                Behavior.ScrollLength(percentage))
        elif method == 'duration':
            self.behaviors.append(
                Behavior.ScrollDuration(duration))

        self.behaviors.append(
            Behavior.ScrollDirection(direction))
