import random as r
from datetime import datetime
from datetime import timedelta
import pytz
import time
import json


class Schedule:
    def __init__(self, interval=60, start_at=32400, end_at=50400,
                 times_set=None):
        self._min_interval = 0.1
        self._p = 0.8
        if type(times_set) is list:
            self._times_set = times_set
        else:
            self._times_set = []
        self._times_blocked = []
        self._slots_exist = None
        self._slots_possible = True
        self.start_at = start_at
        self.end_at = end_at
        self._times_free = [(self.start_at, self.end_at)]
        self.interval = interval
        if len(self._times_set) != 0:
            self._update_blocked()
        else:
            self._slots_exist = True

    @property
    def times_set(self):
        return self._times_set

    @property
    def times_blocked(self):
        return self._times_blocked

    @property
    def times_free(self):
        return self._times_free

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, val):
        if not (type(val) is float or type(val) is int):
            raise TypeError(f'interval should be numeric ')
        elif val < 0:
            raise ValueError(f'interval should be >= 0 received {val}')
        else:
            self._interval = val
        if len(self._times_set) != 0:
            self._update_blocked()

    def new_time(self):
        while not self._slots_exist and self._slots_possible and self.interval * self._p >= self._min_interval:
            self.interval *= self._p
            self._update_blocked()
        if not self._slots_exist:
            self._slots_possible = False
            raise Exception(
                'There are no free slots available, change min interval or remove fixed intervals')
        weights = [abs(b - a) for b, a in self._times_free]
        interval = r.choices(self._times_free, weights=weights, k=1)[0]
        t = r.uniform(interval[0], interval[1])
        self.add_time(t)
        return t

    def add_time(self, t):
        self._times_set.append(t)
        self._times_set.sort()
        self._update_blocked()

    def _update_blocked(self):
        blocked_times_unclean = [(t - self.interval, t + self.interval) for t in
                                 self.times_set]
        if len(blocked_times_unclean) == 0:
            return []
        blocked_times = []
        previous_min, previous_max = blocked_times_unclean[0]
        for interval_min, interval_max in blocked_times_unclean:
            if previous_max >= interval_min:
                previous_max = max(interval_max, previous_max)
            else:
                blocked_times.append((previous_min, previous_max))
                previous_min = interval_min
                previous_max = interval_max

        blocked_times.append((previous_min, previous_max))
        self._times_blocked = blocked_times

        self._slots_exist, free_slots = self._update_free()

        return blocked_times

    def _update_free(self, start=None, end=None):
        if start is not None:
            start = max(start, self.start_at)
        else:
            start = self.start_at
        if end is not None:
            end = min(end, self.end_at)
        else:
            end = self.end_at
        free_slots = []
        if len(self._times_blocked) == 0:
            free_slots.append((start, end))
            times_exist = True
        elif len(self._times_blocked) == 1 and end <= \
                self.times_blocked[0][1] and start >= \
                self.times_blocked[0][0]:
            free_slots = []
            self._times_free = []
            times_exist = False
        else:
            free_slots = []
            previous_max = min(self._times_blocked[0][0] - 1, start)
            for interval_min, interval_max in self.times_blocked:
                if end < previous_max:
                    break
                if start > interval_min:
                    previous_max = interval_max
                    continue
                if end <= interval_min:
                    interval_min = end
                if previous_max <= start:
                    previous_max = start
                free_slots.append((previous_max, interval_min))

                previous_max = interval_max
            if end > previous_max:
                free_slots.append((previous_max, end))

            times_exist = len(free_slots)
        self._times_free = free_slots
        return times_exist, free_slots


class IndividualSchedule(Schedule):
    def __init__(self, global_schedule, interval=60, start_at=0, end_at=86400,
                 times_set=None):
        super().__init__(interval, start_at, end_at, times_set)
        self._global_schedule = global_schedule
        self._slots_cant_exist = False
        self._update_blocked()

    def update(self):
        self._update_blocked()

    def new_time(self):
        self._update_blocked()
        if self._slots_cant_exist:
            self._slots_possible = False
            raise Exception(
                'There are no free slots available, change or remove fixed intervals')
        while not self._slots_exist and self._slots_possible and self._global_schedule.interval * self._p >= self._min_interval:
            self._global_schedule.interval *= self._p
            self._update_blocked()
        if not self._slots_exist:
            self._slots_possible = False
            raise Exception(
                'There are no free slots available, change min interval or remove fixed intervals')
        weights = [abs(b - a) for b, a in self._times_free]
        interval = r.choices(self._times_free, weights=weights, k=1)[0]
        t = r.uniform(interval[0], interval[1])
        self._global_schedule.add_time(t)
        self.add_time(t)
        return t

    def _update_blocked(self):
        super()._update_blocked()
        if not self._slots_exist:
            self._slots_cant_exist = True
            return [(self.start_at, self.end_at)]
        else:
            blocked_times_unclean = self._times_blocked + self._global_schedule.times_blocked
            blocked_times_unclean.sort()
            if len(blocked_times_unclean) == 0:
                return []
            blocked_times = []
            previous_min, previous_max = blocked_times_unclean[0]
            for interval_min, interval_max in blocked_times_unclean:

                if previous_max >= interval_min:
                    previous_max = max(interval_max, previous_max)
                else:
                    blocked_times.append((previous_min, previous_max))
                    previous_min = interval_min
                    previous_max = interval_max

            blocked_times.append((previous_min, previous_max))
            self._times_blocked = blocked_times

            self._slots_exist, free_slots = self._update_free(start=self._global_schedule.start_at,
                                                              end=self._global_schedule.end_at)
        return blocked_times


class TimeHandler:
    with open("resources/other/geosurf_cities.json", 'r') as file:
        LOC_TIMEZONE_DICT = json.load(file)

    def __init__(self,
                 global_schedule,
                 location,
                 wake_time,
                 bed_time,
                 interval=600,
                 server_tz=time.tzname[0]):
        """
        :param global_schedule:
        :param location: geosurf proxy location
        :param wake_time: time in seconds when bot is to wake up e.g. 8:00 = 28800
        :param bed_time: time in seconds when bot is to sleep e.g. 8:00 = 28800
        """
        self._global_schedule = global_schedule
        self._location = location
        self._tz = TimeHandler.LOC_TIMEZONE_DICT.get(self._location)
        self._server_tz = server_tz
        utc_offset = pytz.timezone(self._tz).utcoffset(datetime.now())
        server_utc_offset = pytz.timezone(server_tz).utcoffset(datetime.now())
        self._second_modifier = - utc_offset.total_seconds() + server_utc_offset.total_seconds()
        self._wake_time = wake_time + self._second_modifier
        self._bed_time = bed_time + self._second_modifier
        self._schedule = IndividualSchedule(
            global_schedule=self._global_schedule,
            interval=interval,
            start_at=self._wake_time,
            end_at=self._bed_time)

    def consecutive_times(self, nr):
        self._schedule.update()
        second_list = [self._schedule.new_time() for i in range(0, nr)]
        second_list.sort()
        time_list = [self._to_iso_time(t) for t in second_list]
        return time_list

    def new_time(self):
        self._schedule.update()
        seconds = self._schedule.new_time()
        return self._to_iso_time(seconds)

    def _to_iso_time(self, t):
        date = datetime.now(pytz.timezone(self._server_tz)).replace(hour=0,
                                                                    minute=0,
                                                                    second=0,
                                                                    microsecond=0)
        t = date + timedelta(seconds=t)
        return t.isoformat()
