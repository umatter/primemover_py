"""
Behavior class and subclasses. These classes represent key value pairs, with
    a created_at and updated_at parameter that is not usually set as well as an optional description.
    The intent is to mirror the behaviors required by primemover_runner and check
    parameter validty and output shape.

Available Classes:
    - Behavior: base class
    - URL: behavior containing a URL
    - Text: behavior containing Text (Type Job)
    - SelectionType: behavior containing the type of html selector to be used
    - Selector: behavior containing some selector
    - DecisionType: behavior specifying how a result is selected
    - ScrollDuration: behavior specifying the time for which to scroll
    - ScrollDirection: behavior controlling scroll direction
    - ScrollLength: behavior controlling scroll length as % of website
    - WaitSecconds: behavior specifying duration of a wait
    - AppendReturn: behavior determening wheter to hit return in Type Job
    - TypingMode: behavior controlling how text is entered
    - TaskBehavior: specifies a macro task that a job is part of
    - FlagBehavior: some additional parameter with the key: 'flag'

J.L. 11.2020
"""

from urllib.parse import urlparse
import math


class Behavior:
    """A base key value pair of name and value
    Subclasses check values and assign descriptions
    Public attributes:
        - name: required argument, sets the 'key', spaces are converted to underscores
        - value: any value, must be coercible to string
        - description: an optional description of the key value pair, useful as the library grows
        - created_at: unused, set by api
        - updated_at: unused, set by api
        - active: unused, in {0,1}, set by api
    Public methods:
        as_dict: returns a dictionary representation of the behavior
    """

    def __init__(self, name: str, value,
                 description="Lorem Ipsum", updated_at=None, created_at=None,
                 active=1):
        self.name = name
        self.description = description
        self.value = value
        self.created_at = created_at
        self.updated_at = updated_at
        self.active = active

    def __str__(self):
        return \
            f'"name": "{self.name}",\n' \
            f'"description": "{self.description}",\n' \
            f'"value": {self.value or ""}}}'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, string):
        string = string.strip().replace(' ', '_')
        # string = string.lower()
        self._name = string

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, desc):
        try:
            self._description = str(desc)
        except:
            raise TypeError('Description must be convertible to type string')

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if val is None:
            self._val = ""
        else:
            self._value = val

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, val):
        if val in {0, 1}:
            self._active = val
        else:
            raise ValueError(f'active must be 0 or 1, got {val}')

    def as_dict(self):
        """ Represent behavior as a dictionary
        Returns:
            dictionary with items name, description and value, other attributes
            are currently ignored
        """
        return {"name": self.name,
                "description": self.description,
                "value": self.value}


class URL(Behavior):
    """
    URL behavior key value pair:
    Public Attributes:
        - url: string that is parsed to see if it is a structurally sound url
        - description: a description of the url, default: "URL"
    """

    def __init__(self, url, description='URL'):
        self.url = url
        super().__init__(name='url', value=self.url, description=description)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, passed_url):
        try:
            result = urlparse(passed_url)
            if all([result.scheme, result.netloc]):
                # passed_url = EscapeStrings(passed_url)
                passed_url = passed_url
                self._url = passed_url
            else:
                raise ValueError(
                    f'{passed_url} does not appear to be a valid URL')
        except:
            raise ValueError(f'{passed_url} does not appear to be a valid URL')


class Text(Behavior):
    """
    Text behavior key value pair, this is used for the Type job
    Public Attributes:
        - text: some string
        - description: a description of the url, default: "Text to enter"
    """

    def __init__(self, text):

        self.text = text
        super().__init__(name='text', value=self.text,
                         description=f'Text to enter')

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, string):
        try:
            self._text = str(string)

        except:
            raise TypeError('Text must be coercable to type string')


class SelectionType(Behavior):
    """
    SelectionType behavior key value pair, used to share the type of some selector
    Public Attributes:
        - selector_type: string, one of "XPATH|CSS|CLASS|ID"
        - description: a description of the url, default: "Type of selection"
    """

    def __init__(self, selector_type):

        self.selector_type = selector_type
        super().__init__(name='selectionType', value=self.selector_type,
                         description=f'Type of selection')

    @property
    def selector_type(self):
        return self._selector_type

    @selector_type.setter
    def selector_type(self, value):
        value = value.upper().strip()
        if value in {'XPATH', 'CSS', 'CLASS', 'ID'}:
            self._selector_type = value
        else:
            raise ValueError(
                f'selector type must be in {{"XPATH", "CSS, "CLASS", "ID"}} got {value} instead.')


class Selector(Behavior):
    """
    Selector behavior key value pair, used to share a html selector
    Public Attributes:
        - selector: string, a valid XPATH|CSS|CLASS|ID selector
        - kind: string, what is the selector? use to specify purpose or type (optional)
    """

    def __init__(self, selector, kind=""):
        self.selector = selector
        self.kind = kind

        super().__init__(name='selector', value=self.selector,
                         description=f'{kind} selector')

    @property
    def selector(self):
        return self._selector

    @selector.setter
    def selector(self, value):
        # self._selector = EscapeStrings(value)
        self._selector = value


class DecisionType(Behavior):
    """
    DecisionType behavior key value pair, used to determine how a result is selected
    Public Attributes:
        - decision_type: string,  one of "FIRST|LAST|RANDOM|CALCULATED"
    """

    def __init__(self, decision_type):
        self.decision_type = decision_type

        super().__init__(name='decisionType', value=self.decision_type,
                         description=f'Decision type for choosing an item out of the list given by the selector is {self.decision_type}',
                         )

    @property
    def decision_type(self):
        return self._decision_type

    @decision_type.setter
    def decision_type(self, value):
        value = value.upper().strip()
        if value in {'FIRST', 'LAST', 'RANDOM', 'CALCULATED'}:
            self._decision_type = value
        else:
            raise ValueError(
                f'decision type must be in {{"FIRST", "LAST, "RANDOM","CLACULATED"}} got {value} instead.')


class ScrollDuration(Behavior):
    """
    ScrollDuration behavior key value pair, used to determine duration of scroll by time
    Public Attributes:
        - duration: int, seconds>0
    """

    def __init__(self, duration: int):

        self.duration = duration
        super().__init__(name='scrollDuration', value=self.duration,
                         description=f'Scroll for {self.duration} seconds.'
                         )

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, d):
        if type(d) is int and d > 0:
            self._duration = d
        elif type(d) is float or d == 0:
            self._duration = int(math.ceil(d))
            if d == 0:
                self._duration = 1
            raise Warning(
                f'Scroll duration expects an integer >0, {d} has been rounded up to {self.duration}')
        else:
            raise TypeError('Scroll duration must be of type int')


class ScrollDirection(Behavior):
    """
    ScrollDirection behavior key value pair, used to determine scroll direction
    Public Attributes:
        - direction: string,  one of "UP/U|DOWN/D" (not case sensitive)
    """
    SCROLL_DESC_DICT = {'UP': 'Scroll up', 'DOWN': 'Scroll down'}

    def __init__(self, direction):
        """
        :param direction: string, either 'UP'/'U' or 'DOWN'/'D'
        """
        self.direction = direction
        description = ScrollDirection.SCROLL_DESC_DICT[self.direction]
        super().__init__(name='scrollDirection',
                         value=self.direction,
                         description=description)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, d):
        try:
            d = d.upper().strip()
        except AttributeError:
            raise TypeError(f'Direction must be of type string')
        if d in ['UP', 'U']:
            self._direction = 'UP'
        elif d in ['DOWN', 'D']:
            self._direction = 'DOWN'
        else:
            raise ValueError(
                f'direction must be in ("U","UP","D","DOWN") received {d}')


class ScrollLength(Behavior):
    """
    ScrollLength behavior key value pair, used to determine scroll length as percentage of website length
    Public Attributes:
        - percentage: numeric in [0,100]
    """

    def __init__(self, percentage):
        self.percentage = percentage
        super().__init__(name='length', value=self.percentage,
                         description=f'Scroll {self.percentage} of window.')

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, d):
        try:
            d = float(d)
        except ValueError:
            raise ValueError(f'Expected numeric, received {d}')
        if 0 <= d <= 100:
            self._percentage = d
        else:
            raise ValueError(f'Duration must be between 0, 100')


class WaitSeconds(Behavior):
    """
    Wait behavior key value pair, used to time a wait period in seconds
    Public Attributes:
        - duration: int, seconds to wait
    """

    def __init__(self, duration):
        """
        :param duration: int >0 time in seconds
        """
        self.duration = duration
        super().__init__(name='seconds', value=self.duration,
                         description=f'Wait for {self.duration} seconds.')

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, d):
        if type(d) is int and d > 0:
            self._duration = d
        elif type(d) is float or d == 0:
            self._duration = int(math.ceil(d))
            if d == 0:
                self._duration = 1
            raise Warning(
                f'Wait duration expects an integer >0, {d} has been rounded up to {self.duration}')
        else:
            raise TypeError('Wait duration must be of type int')


class AppendReturn(Behavior):
    """
    AppendReturn behavior key value pair, used to determine wheter to hit return in type job
    Public Attributes:
        - send_return, boolean
    """

    def __init__(self, send_return=False):
        self.send_return = send_return
        super().__init__(name='appendReturn', value=self.send_return,
                         description=f'Optional field: appends a return key after the text given if true.')

    @property
    def send_return(self):
        return self._send_return

    @send_return.setter
    def send_return(self, val):
        if type(val) is str:
            val = val.strip().lower()
            if val == 'false':
                self._send_return = False
            elif val == 'true':
                self._send_return = True
            else:
                raise ValueError(
                    f'send_return must be true/false, recived {val}')
        elif type(val) is bool:
            self._send_return = val
        else:
            raise TypeError(
                f'send_return must be type bool or a string "true"/"false", received {val}')


class TypingMode(Behavior):
    """Controls the method by which text is typed
    Public attributes:
    -mode: str, in {"DIRECT","SIMULATED_KEEPINGTYPOS","SIMULATED_FIXINGTYPOS","SIMULATED_NOTYPOS"}
            Direct: send keys at once (imagine copy and paste)
            Simulated_KeepingTypos: Simulate key presses, make typos and keep some of them
            Simulated_FixingTypos: Simulate key presses, make typos fix all of them
            Simulated_NoTypos: Simulate key presses, make no mistakes  (default argument)
    """

    def __init__(self, mode="SIMULATED_NOTYPOS"):
        self.mode = mode
        super().__init__(name='typingMode', value=self.mode,
                         description=f'Optional field: How the text is entered into the field')

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, val):
        if type(val) is str:
            val.strip().upper()
            if val in {"DIRECT", "SIMULATED_KEEPINGTYPOS",
                       "SIMULATED_FIXINGTYPOS", "SIMULATED_NOTYPOS"}:
                self._mode = val
            else:
                raise ValueError(
                    f'send_return must be one of {{"DIRECT","SIMULATED_KEEPINGTYPOS","SIMULATED_FIXINGTYPOS","SIMULATED_NOTYPOS"}}, got {val}')
        else:
            raise TypeError(
                f'mode must be type str')


class TaskBehavior(Behavior):
    """
    TaskBehavior behavior key value pair, used to indicate a larger task that a job is a part off. This is always optional.
    Public Attributes:
        - task, task name (determined by primemover_py
    """

    def __init__(self, task):
        self.task = task
        super().__init__(name='task', value=self.task,
                         description=f'This job is part of the task {self.task} ')

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, val):
        if type(val) is str:
            self._task = val
        else:
            raise TypeError(
                f'task must be type str')


class FlagBehavior(Behavior):
    """
    FlagBehavior behavior key value pair, used to indicate additional info about a job. This is always optional.
    Public Attributes:
        - flag, some flag to pass
    """

    def __init__(self, flag):
        self.flag = flag
        super().__init__(name='flag', value=self.flag,
                         description="")

    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, val):
        self._flag = val


class CaptchaMode(Behavior):
    """
        input: str, one of { 'always', 'never', 'random'} default = 'never'
            always -> always attempt to solve captchas when they occur
            never -> never attempt to solve captchas, proceed as if none exists
            random -> randomly attempt solve
        can be appended to any job, is not required?
    """

    def __init__(self, mode='never'):
        self.mode = mode
        super().__init__(name='captchaMode', value=self.mode,
                         description="")

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, val):
        if type(val) is str:
            val = val.strip().lower()
        else:
            raise TypeError('Expected string')
        if val in {'always', 'never', 'random'}:
            self._mode = val
        elif val == "":
            self._mode = 'never'
        else:
            raise ValueError(f'Mode must be one of: [ always, never, random] received {val}')
