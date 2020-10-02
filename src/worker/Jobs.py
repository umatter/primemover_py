import src.worker.Behavior as Behavior


class Job:

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

    def __str__(self):
        job_descr = \
            f'"name": "{self._name or ""}",\n' \
            f'"type":"{self.type or ""}",\n' \
            f'"description": "{self._description or ""}"'
        formatted = ",\n".join([str(x) for x in self.behaviors])
        return f'{{{job_descr},"behaviors": [\n{formatted}]}}'

    def as_dict(self):
        return {
            "name": self._name,
            "type": self.type,
            "description": self._description,
            "behaviors": [x.as_dict() for x in self.behaviors]}


class VisitJob(Job):
    def __init__(self, url,
                 task=None,
                 flag=None):
        """
        :param url: A valid URL to visit
        """
        super().__init__(job_type='visitjob', name='Visit',
                         description=f'Visit {url}', task=task, flag=flag)
        self.behaviors.append(Behavior.URL(url))


class Wait(Job):
    def __init__(self, time,
                 task=None,
                 flag=None):
        """
        :param time: Wait time in seconds
        :param start_at:
        """
        super().__init__(job_type='waitjob', name='Wait',
                         description=f'Wait for {time} seconds', task=task, flag=flag)
        self.behaviors.append(
            Behavior.WaitSeconds(time))


class EnterText(Job):
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
        :param text:
        :param selector:
        :param send_return:
        :param type_mode:
        :param selector_type:
        """
        super().__init__(job_type='entertextfieldjob',
                         name='Enter Text',
                         description=f'Enter text into the defined field', task=task, flag=flag)
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
    def __init__(self, selector, selector_type='XPATH',
                 decision_type='FIRST',
                 task=None,
                 flag=None):
        """
        :param selector:
        :param selector_type:
        :param decision_type:
        """
        super().__init__(job_type='singleselecturljob',
                         name='Select',
                         description=f'Select an item and click', task=task, flag=flag)
        self.behaviors.append(
            Behavior.SelectionType(selector_type))
        self.behaviors.append(
            Behavior.Selector(selector))
        self.behaviors.append(
            Behavior.DecisionType(decision_type))


class TryClick(Job):
    def __init__(self, selector, selector_type='XPATH',
                 task=None,
                 flag=None ):
        """
        :param selector:
        :param selector_type:
        """
        super().__init__(job_type='tryclickjob',
                         name='Try Click',
                         description=f'Try to click a button/item', task=task, flag=flag)
        self.behaviors.append(
            Behavior.SelectionType(selector_type))
        self.behaviors.append(
            Behavior.Selector(selector))


class Scroll(Job):
    def __init__(self, direction='DOWN', duration=None,
                 percentage=None,
                 task=None,
                 flag=None):
        """
            :param direction:
            :param duration: int
            :param length:
            """
        if percentage is not None:
            method = 'length'
        elif duration is not None:
            method = 'duration'
        else:
            raise ValueError('One of duration and length must be set')

        super().__init__(job_type=f'scrollby{method}job',
                         name=f'Scroll by {method}',
                         description=f'Scroll {direction.lower()}', task=task, flag=flag)
        if method == 'length':
            self.behaviors.append(
                Behavior.ScrollLength(percentage))
        elif method == 'duration':
            self.behaviors.append(
                Behavior.ScrollDuration(duration))

        self.behaviors.append(
            Behavior.ScrollDirection(direction))
