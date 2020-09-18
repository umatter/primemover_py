from urllib.parse import urlparse

from src.Utilities import *


class Behavior:
    def __init__(self, name, value,
                 description="Lorem Ipsum", updated_at=None, created_at=None):
        self.name = name
        self.description = description
        self.value = value
        self.created_at = created_at
        self.updated_at = updated_at

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
            raise TypeError('Description must be convertible to kind string')

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

        return {"name": self.name,
                "description": self.description,
                "value": self.value}


class URL(Behavior):
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
    def __init__(self, text):
        """
        :param string: text to type into a field
        """
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
            raise TypeError('Text must be coercable to kind string')


class SelectionType(Behavior):
    def __init__(self, selector_type):
        """
        :param selector_type: string, one of "XPATH|CSS|CLASS|ID"
        """
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
    def __init__(self, selector, kind=""):
        """
        :param selector: a valid selector one of "XPATH|CSS|CLASS|ID"
        """
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
    def __init__(self, decision_type):
        """
        :param decision_type: string, one of "FIRST|LAST|RANDOM"
        """
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
        if value in {'FIRST', 'LAST', 'RANDOM'}:
            self._decision_type = value
        else:
            raise ValueError(
                f'decision type must be in {{"FIRST", "LAST, "RANDOM"}} got {value} instead.')


class ScrollDuration(Behavior):
    def __init__(self, duration):
        """
        :param duration: float >0 time in seconds
        """
        self.duration = duration
        super().__init__(name='scrollDuration', value=self.duration,
                         description=f'Scroll for {self.duration} seconds.'
                         )

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, d):
        try:
            d = float(d)
        except ValueError:
            raise ValueError(f'Expected numeric, received {d}')
        if d <= 0:
            raise ValueError(f'Duration must be > 0')
        else:
            self._duration = d


class ScrollDirection(Behavior):
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
    def __init__(self, percentage):
        """
        :param percentage: float in [0,100] percentage of window to scroll down
        """
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
    def __init__(self, duration):
        """
        :param duration: float >0 time in seconds
        """
        self.duration = duration
        super().__init__(name='seconds', value=self.duration,
                         description=f'Wait for {self.duration} seconds.')

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, d):
        try:
            d = float(d)
        except ValueError:
            raise ValueError(f'Expected numeric, received {d}')
        if d <= 0:
            raise ValueError(f'Duration must be > 0')
        else:
            self._duration = d


class AppendReturn(Behavior):
    def __init__(self, send_return=False):
        """
        :param send_return: bool or str "true/false"
        """
        self.send_return = send_return
        super().__init__(name='appendReturn', value=self.send_return,
                         description=f'Optional field: appends a return key after the text given if true.')

    @property
    def send_return(self):
        return self._send_return

    @send_return.setter
    def send_return(self, val):
        if type(val) is str:
            val.strip().lower()
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
    def __init__(self, mode="SIMULATED_NOTYPOS"):
        """
        :param mode: str, in {"DIRECT","SIMULATED_KEEPINGTYPOS","SIMULATED_FIXINGTYPOS","SIMULATED_NOTYPOS"}
        Direct: send keys at once (imagine copy and paste)
        Simulated_KeepingTypos: Simulate key presses, make typos and keep some of them
        Simulated_FixingTypos: Simulate key presses, make typos fix all of them
        Simulated_NoTypos: Simulate key presses, make no mistakes
        """
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
            if val in {"DIRECT","SIMULATED_KEEPINGTYPOS","SIMULATED_FIXINGTYPOS","SIMULATED_NOTYPOS"}:
                self._mode = val
            else:
                raise ValueError(
                    f'send_return must be one of {{"DIRECT","SIMULATED_KEEPINGTYPOS","SIMULATED_FIXINGTYPOS","SIMULATED_NOTYPOS"}}, got {val}')
        else:
            raise TypeError(
                f'mode must be type str')
