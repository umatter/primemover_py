from urllib.parse import urlparse

import datetime


class Behavior:
    def __init__(self, name, value, active=1, description="Lorem Ipsum"):
        self.name = name
        self.description = description
        self.value = value
        self.active = active


    def __str__(self):
        return \
            f'{{"name": "{self.name}",\n' \
            f'"description": "{self.description}",\n' \
            f'"value": {self.value},\n' \
            f'"active": {self.active}}}'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, string):
        string = string.lower().strip().replace(' ', '_')
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
        if type(val) is str:
            self._value = f'"{val}"'

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, val):
        if val in {0, 1}:
            self._active = val
        else:
            raise ValueError(f'active must be 0 or 1, got {val}')


class JobType(Behavior):
    def __init__(self, description='', active=1):
        self.description = description
        self.type = description
        super().__init__(name='job_type', value=self.type,
                         description=description,
                         active=active)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, desc):
        self._description = desc

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        self._type = val.strip().lower().replace(' ', '_')


class URL(Behavior):
    def __init__(self, url, description='URL', active=1):
        self.url = url
        super().__init__(name='url', value=self.url, description=description,
                         active=active)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, passed_url):
        try:
            result = urlparse(passed_url)
            if all([result.scheme, result.netloc]):
                self._url = passed_url
            else:
                raise ValueError(
                    f'{passed_url} does not appear to be a valid URL')
        except:
            raise ValueError(f'{passed_url} does not appear to be a valid URL')


class StartTime(Behavior):
    def __init__(self, start_time, active=1):
        """
        :param time: string of shape Datetime.Datetime.isoformat This is not the
            actual isoformat! It does not include the timezone!
        """
        self.start_time = start_time
        super().__init__(name='start_at', value=self.start_time,
                         description='Start Job at...', active=active)

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, t):
        t = t.rep('Z', '')
        try:
            datetime.datetime.fromisoformat(t)
            self._start_time = t + 'Z'
        except:
            raise ValueError(f'{t} does not meet the Datetime isoformat')


class ScrollDirection(Behavior):
    SCROLL_DESC_DICT = {'up': 'Scrowl up', 'down': 'Scrowl down'}

    def __init__(self, direction, active=1):
        """
        :param direction: string, either 'up'/'u' or 'down'/'d'
        """
        self.direction = direction
        self._description = ScrollDirection.SCROLL_DESC_DICT[self.direction]
        super().__init__(name='direction', value=self.direction, description='',
                         active=active)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, d):
        try:
            d = d.lower().strip()
        except AttributeError:
            raise TypeError(f'Direction must be of type string')
        if d in ['up', 'u']:
            self._direction = 'up'
        elif d in ['down', 'd']:
            self._direction = 'down'
        else:
            raise ValueError(
                f'direction must be in ("u","up","d","down") received {d}')


class ScrollDistance(Behavior):

    def __init__(self, distance, active=1):
        """
        :param length: int
        """
        self.distance = distance
        super().__init__(name='length', value=self.distance,
                         description='Keep scrolling until.',
                         active=active)

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, d):
        try:
            self._distance = int(d)
        except ValueError:
            raise ValueError(f'Expected numeric, received {d}')


class ScrollDuration(Behavior):
    def __init__(self, duration, active=1):
        """
        :param length: float >0
        """
        self.duration = duration
        super().__init__(name='duration', value=self.duration,
                         description=f'Scroll for {self.duration} seconds.',
                         active=active)

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


class Field(Behavior):
    def __init__(self, name, active=1):
        """
        :param string: field
        """
        self.name = name
        super().__init__(name='field', value=self.name,
                         description=f'Name of the field is {self.name}.',
                         active=active)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, string):
        try:
            self._name = string.lower().strip()
        except AttributeError:
            raise TypeError(f'Name must be of typee string')


class Text(Behavior):
    def __init__(self, text, active=1):
        """
        :param string: text to type into a field
        """
        self.text = text
        super().__init__(name='text', value=self.text,
                         description=f'Enter {self.text} into Field',
                         active=active)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, string):
        try:
            self._text = str(string)

        except:
            raise TypeError('Text must be coercable to kind string')


class Username(Behavior):
    def __init__(self, user, active=1):
        """
        :param string: Username
        """
        self.user = user
        super().__init__(name='username', value=self.user,
                         description=f'Username is {self._user}',
                         active=active)

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, string):
        try:
            self._user = str(string)

        except:
            raise TypeError('user must be coercable to type string')


class Password(Behavior):
    def __init__(self, password, active=1):
        """
        :param string: Password
        """
        self.password = password
        super().__init__(name='password', value=self.password,
                         description=f'Username is {self._password}',
                         active=active)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, string):
        try:
            self._password = str(string)

        except:
            raise TypeError('password must be coercable to kind string')


class XPath(Behavior):
    def __init__(self, x_path, kind=None, active=1):
        """
        :param x_path of some object or field
        """
        self.kind = kind
        self.x_path = x_path
        if self.kind is not None:
            name = f'x_path_{kind}'
        else:
            name = 'x_path'
        super().__init__(name=name, value=self.x_path,
                         description="",
                         active=active)

    @property
    def x_path(self):
        return self._x_path

    @x_path.setter
    def x_path(self, string):
        try:
            self._x_path = str(string)

        except:
            raise TypeError('x_path must be coercible to kind string')

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, string):
        try:
            self._kind = str(string)

        except:
            raise TypeError('kind must be coercible to kind string')


class CSS(Behavior):
    def __init__(self, css, kind=None, active=1):
        """
        :param x_path of some object or field
        """
        self.css = css
        self.kind = kind
        if self.kind is not None:
            name = f'css_{kind}'
        else:
            name = 'css'

        super().__init__(name=name, value=self.css,
                         description="",
                         active=active)

    @property
    def css(self):
        return self._css

    @css.setter
    def css(self, string):
        try:
            self._css = str(string)

        except:
            raise TypeError('css must be coercible to type string')

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, string):
        try:
            self._kind = str(string)

        except:
            raise TypeError('kind must be coercible to type string')


class Duration(Behavior):
    def __init__(self, min_duration, max_duration, active=1):
        """
        :param min_duration: min nr. seconds to wait
        :param max_duration: max nr. seconds to wait
        """
        self.min_duration = (min_duration, max_duration)
        self.max_duration = (min_duration, max_duration)

        super().__init__(name='duration',
                         value=[self.min_duration, self.max_duration],
                         description="",
                         active=active)

    @property
    def min_duration(self):
        return self._min_duration

    @min_duration.setter
    def min_duration(self, vals):
        val_1, val_2 = vals
        try:
            min_val = min(val_1, val_2)
        except:
            raise ValueError('Min duration must be numeric >0')

        if min_val >= 0:
            self._min_duration = min_val
        else:
            raise ValueError('Min duration must be >= 0')

    @property
    def max_duration(self):
        return self._max_duration

    @max_duration.setter
    def max_duration(self, vals):
        val_1, val_2 = vals
        try:
            max_val = max(val_1, val_2)
        except:
            raise ValueError('Max duration must be numeric >0')

        if max_val >= 0:
            self._max_duration = max_val
        else:
            raise ValueError('Max duration must be >= 0')


class PauseInterval(Behavior):
    def __init__(self, min_duration, max_duration, active=1):
        """
        :param min_duration: min nr. seconds to wait
        :param max_duration: max nr. seconds to wait
        """
        self.min_duration = (min_duration, max_duration)
        self.max_duration = (min_duration, max_duration)

        super().__init__(name='pause_interval',
                         value=[self.min_duration, self.max_duration],
                         description="Pause Interval",
                         active=active)

    @property
    def min_duration(self):
        return self._min_duration

    @min_duration.setter
    def min_duration(self, vals):
        val_1, val_2 = vals
        try:
            min_val = min(val_1, val_2)
        except:
            raise ValueError('Min duration must be numeric >0')

        if min_val >= 0:
            self._min_duration = min_val
        else:
            raise ValueError('Min duration must be >= 0')

    @property
    def max_duration(self):
        return self._max_duration

    @max_duration.setter
    def max_duration(self, vals):
        val_1, val_2 = vals
        try:
            max_val = max(val_1, val_2)
        except:
            raise ValueError('Max duration must be numeric >0')

        if max_val >= 0:
            self._max_duration = max_val
        else:
            raise ValueError('Max duration must be >= 0')


class NoOfScrolls(Behavior):

    def __init__(self, no_of_scrolls, active=1):

        self.no_of_scrolls = no_of_scrolls
        super().__init__(name='no_of_scrolls', value=self.distance,
                         description=f'Repeat {self.no_of_scrolls} times.',
                         active=active)

    @property
    def distance(self):
        return self._no_of_scrolls

    @distance.setter
    def distance(self, nr):
        try:
            self._no_of_scrolls = int(nr)
        except ValueError:
            raise ValueError(f'Expected numeric, received {nr}')


class ActiveProbability(Behavior):
    def __init__(self, prob, active=1):

        self.probability = prob
        super().__init__(name='active_probability', value=self.probability,
                         description="",
                         active=active)

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, prob):
        if 0 <= prob <= 1:
            self._probability = prob
        else:
            raise ValueError(f'probability must be in [0,1]')


class UrlId(Behavior):
    def __init__(self, url_id, kind="", active=1):
        self.url_id = url_id
        super().__init__(name=f'{kind}_url_id', value=self.url_id,
                         description="URL ID",
                         active=active)

    @property
    def url_id(self):
        return self._url_id

    @url_id.setter
    def url_id(self, id):
        self._url_id = id
