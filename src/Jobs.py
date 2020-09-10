import src.Behavior as Behavior
from src.Info import *


class Job:

    def __init__(self,
                 job_info,
                 job_type,
                 name="",
                 description="",
                 ):
        self.job_info = job_info
        self.type = job_type
        self._description = description
        self._name = name
        self.behaviors = []

    # @property
    # def behaviors(self):
    #     return self._behaviors
    #
    # @behaviors.setter
    # def behaviors(self, behavior_list):
    #     is_valid = [type(behavior) for behavior in behavior_list]
    #     if Behavior. not in type_list:
    #         raise ValueError(
    #             'The first element of behviors must be of class JobType')
    #     else:
    #         self._behaviors = behavior_list

    @property
    def job_info(self):
        return self._job_info

    @job_info.setter
    def job_info(self, info):
        if not type(info) is JobInfo:
            raise TypeError('job_info must be of type JobInfo')
        else:
            self._job_info = info

    def __str__(self):
        job_descr = \
            f'"id": {self.job_info.job_id or ""},\n' \
            f'"user_id":" {self.job_info._user_id or ""}",\n' \
            f'"queue_id": {self.job_info.queue_id or ""},\n' \
            f'"name": "{self._name or ""}",\n' \
            f'"type":"{self.type or ""}",\n' \
            f'"description": "{self._description or ""}",\n' \
            f'"started": {self.job_info.started},\n' \
            f'"success": {self.job_info.success},\n' \
            f' "failure": {self.job_info.failure},\n' \
            f'"order": {self.job_info.order},\n' \
            f'"active": {self.job_info.active}'
        formatted = ",\n".join([str(x) for x in self.behaviors])
        return f'{{{job_descr},"behaviors": [\n{formatted}]}}'


class VisitJob(Job):
    def __init__(self, job_info, url):
        """
        :param url: A valid URL to visit
        :param job_info:
        """
        super().__init__(job_info=job_info, job_type='visitjob', name='Visit',
                         description=f'Visit {url}')
        self.behaviors.append(Behavior.URL(url, self.job_info.new_behavior()))


class Wait(Job):
    def __init__(self, job_info, time):
        """
        :param time: Wait time in seconds
        :param job_info:
        :param start_at:
        """
        super().__init__(job_info=job_info, job_type='waitjob', name='Wait',
                         description=f'Wait for {time} seconds')
        self.behaviors.append(
            Behavior.WaitSeconds(time, self.job_info.new_behavior()))


class EnterText(Job):
    def __init__(self, job_info, text, selector, selector_type='XPATH'):
        """
        :param job_info:
        :param text:
        :param selector:
        :param selector_type:
        """
        super().__init__(job_info=job_info, job_type='entertextfieldjob',
                         name='Enter Text',
                         description=f'Enter text into the defined field')
        self.behaviors.append(Behavior.Text(text, self.job_info.new_behavior()))
        self.behaviors.append(
            Behavior.SelectionType(selector_type, self.job_info.new_behavior()))
        self.behaviors.append(
            Behavior.Selector(selector, self.job_info.new_behavior()))


class SingleSelect(Job):
    def __init__(self, job_info, selector, selector_type='XPATH',
                 decision_type='FIRST'):
        """
        :param job_info:
        :param selector:
        :param selector_type:
        :param decision_type:
        """
        super().__init__(job_info=job_info, job_type='singleselecturljob',
                         name='Select',
                         description=f'Select an item and click')
        self.behaviors.append(
            Behavior.SelectionType(selector_type, self.job_info.new_behavior()))
        self.behaviors.append(
            Behavior.Selector(selector, self.job_info.new_behavior()))
        self.behaviors.append(
            Behavior.DecisionType(decision_type, self.job_info.new_behavior()))


class TryClick(Job):
    def __init__(self, job_info, selector, selector_type='XPATH', ):
        """
        :param job_info:
        :param selector:
        :param selector_type:
        """
        super().__init__(job_info=job_info, job_type='tryclickjob',
                         name='Try Click',
                         description=f'Try to click a button/item')
        self.behaviors.append(
            Behavior.SelectionType(selector_type, self.job_info.new_behavior()))
        self.behaviors.append(
            Behavior.Selector(selector, self.job_info.new_behavior()))


class Scroll(Job):
    def __init__(self, job_info, direction='DOWN', duration=None,
                 percentage=None):
        """
            :param job_info:
            :param direction:
            :param duration:
            :param length:
            """
        if percentage is not None:
            method = 'length'
        elif duration is not None:
            method = 'duration'
        else:
            raise ValueError('One of duration and length must be set')

        super().__init__(job_info=job_info, job_type=f'scrollby{method}job',
                         name=f'Scroll by {method}',
                         description=f'Scroll {direction.lower()}')
        if method == 'length':
            self.behaviors.append(
                Behavior.ScrollLength(percentage, self.job_info.new_behavior()))
        elif method == 'duration':
            self.behaviors.append(
                Behavior.ScrollDuration(duration, self.job_info.new_behavior()))

        self.behaviors.append(
            Behavior.ScrollDirection(direction, self.job_info.new_behavior()))
