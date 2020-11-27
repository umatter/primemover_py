"""
Profile defines the profile class, this mirrors the setup for multilogin.
J.L. - 11/2020
"""

from webob import acceptparse
import json


class Profile:
    def __init__(self,
                 name="%%AGENTID%%",
                 os='win',
                 browser='stealthfox',
                 language="en-us",
                 geolocation='DEFAULT',
                 do_not_track='DEFAULT',
                 hardware_canvas='DEFAULT',
                 local_storage='DEFAULT',
                 service_worker_cache='DEFAULT'):
        """
        Arguments
            - name: some string, defaults to placeholder for agent_id
            - os:  an os, must be in {'win', 'mac', 'linux', 'android'}
            - browser: must be in {'mimic', 'stealthfox', 'mimic_mobile'}
                mimic_mobile is only available when os is 'android'
            - language: string containing language and if desired preference for language
                e.g. 'en-US;q=0.8, it;q=0.1, fr-CA;q=0.1' (<language>-<region>;<preference>)
                only <language> is required e.g. ('en, it'). Websites should adjust according
                to these preferences. 'DEFAULT' will allow multilogin to set
            - geolocation: string in { PROMPT, BLOCK, ALLOW }, Note, Prompt is perhaps undesirable
                since it requires additional browser automation to accept. 'DEFAULT' will allow multilogin to set (default: 'DEFAULT')
            - do_not_track: 1,0 if 1, doNotTrack is on, else off. 'DEFAULT' will allow multilogin to set
            - hardware_canvas: one of [ REAL, BLOCK, NOISE ]. 'DEFAULT' will allow multilogin to set
            - local_storage: boolean, default:'DEFAULT' will allow multilogin to set. If local_storage is False, service_worker_cache is set to False
            - service_worker_cache: boolean, default: 'DEFAULT' will allow multilogin to set. If local_storage is False, service_worker_cache can not be set to True
        """
        self.os = os
        self.name = name
        self.browser = browser
        self.language = language
        self.geolocation = geolocation
        self.do_not_track = do_not_track
        self.hardware_canvas = hardware_canvas
        self.local_storage = local_storage
        self.service_worker_cache = service_worker_cache

    @property
    def os(self):
        return self._os

    @os.setter
    def os(self, string: str):
        """
        Check validity of operating system and set self._os
        Arguments:
            - string: name of an os, must be in {'win', 'mac', 'linux', 'android'}
        Exceptions:
            - ValueError: raises a value error when string is not an os accepted by MultiLogin
        """
        string = string.strip().lower()
        valid_os = {'win', 'mac', 'linux', 'android'}
        if string in valid_os:
            self._os = string
        else:
            raise ValueError(
                f'os must be one off {valid_os}, received {string}')

    @property
    def browser(self):
        return self._browser

    @browser.setter
    def browser(self, string: str):
        """
        Check validity of browser  and set self._browser
        Arguments:
            - string: name of browser, must be in {'mimic', 'stealthfox', 'mimic_mobile'}
                mimic_mobile is only available when os is 'android'
        Exceptions:
            - ValueError: raises a value error when string is not a browser accepted by MultiLogin

        """
        string = string.strip().lower()
        non_mobile = {'mimic', 'stealthfox'}
        if string in non_mobile:
            self._browser = string
        elif string == 'mimic_mobile':
            if self.os != 'android':
                raise ValueError(
                    'browser mimic_mobile is only available when os is android, please change the os or browser')
        else:
            raise ValueError(
                f'os must be one off {non_mobile} or android, received {string}')

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, language_string: str):
        """
        language_string: string containing language and if desired preference for different languages
                e.g. 'en-US;q=0.8, it;q=0.1, fr-CA;q=0.1' (<language>-<region>;<preference>)
                only <language> is required e.g. ('en, it')"""
        if language_string == 'DEFAULT':
            self._language = None
        else:
            accept_header = acceptparse.create_accept_language_header(language_string)
            if type(accept_header) is acceptparse.AcceptLanguageValidHeader:
                self._language = language_string
            else:
                raise ValueError('language string is not correctly formatted')

    @property
    def geolocation(self):
        return self._geolocation

    @geolocation.setter
    def geolocation(self, string: str):
        """
        Check validity of geolocation setting and set self._geolocation
        Arguments:
            - string: desired setting {PROMPT, BLOCK, ALLOW, DEFAULT}
                DEFAULT -> NONE
        Exceptions:
            - ValueError: raises a value error when string is not a setting accepted by MultiLogin
        """
        string = string.strip().upper()
        valid_settings = {'PROMPT', 'BLOCK', 'ALLOW'}
        if string == 'DEFAULT':
            self._geolocation = None
        elif string in valid_settings:
            self._geolocation = string
        else:
            raise ValueError(
                f'os must be one off {valid_settings}, received {string}')

    @property
    def do_not_track(self):
        return self._do_not_track

    @do_not_track.setter
    def do_not_track(self, value: int):
        if value == 'DEFAULT':
            self._do_not_track = None
        elif value in {1, 0}:
            self._do_not_track = value
        else:
            raise ValueError(f'do_not_track must be 1 or 0 received {value}')

    @property
    def local_storage(self):
        return self._local_storage

    @local_storage.setter
    def local_storage(self, value):
        if value == 'DEFAULT':
            self._local_storage = None
        elif type(value) is str:
            value = value.strip().lower()
            if value == 'true':
                self._local_storage = True
            elif value == 'false':
                self._local_storage = False
                self.service_worker_cache = False
        elif value:
            self._local_storage = value
        elif not value:
            self._local_storage = False
            self.service_worker_cache = False
        else:
            raise ValueError('Invalid local storage value')

    @property
    def service_worker_cache(self):
        return self._service_worker_cache

    @service_worker_cache.setter
    def service_worker_cache(self, value):
        if value == 'DEFAULT':
            self._service_worker_cache = None
        elif type(value) is str:
            value = value.strip().lower()
            if value == 'true':
                self._service_worker_cache = True
                if self._local_storage is False:
                    raise Exception(
                        'Attempting to set serviceWorkerCache True, while local storage is False')
            elif value == 'false':
                self._local_storage = False
                self._service_worker_cache = False
        elif value:
            self._service_worker_cache = value
            if self._local_storage is False:
                raise Exception(
                    'Attempting to set serviceWorkerCache True, while local storage is False')
        elif not value:
            self._local_storage = False
            self._service_worker_cache = False
        else:
            raise ValueError('Invalid serviceWorkerCache value')

    @property
    def hardware_canvas(self):
        return self._hardware_canvas

    @hardware_canvas.setter
    def hardware_canvas(self, value):
        if value == 'DEFAULT':
            self._hardware_canvas = None
        else:
            value = value.strip().upper()
            if value in {'REAL', 'BLOCK', 'NOISE'}:
                self._hardware_canvas = value
            else:
                raise ValueError(
                    f'Invalid hardware_canvas setting, should be one of REAL,BLOCK, NOISE')

    def as_dict(self):
        base_dict = {
            "name": self.name,
            "os": self.os,
            "browser": self.browser,
            "network": {
                "proxy": {
                    "type": "%%PROXYTYPE%%",
                    "host": "%%PROXYHOST",
                    "port": "%%PROXYPORT%%",
                    "username": "%%PROXYUSERNAME%%",
                    "password": "%%PROXYPASSWORD%%"
                },
                "dns": []
            }
        }
        if self.language is not None:
            base_dict['navigator'] = {'language': self.language}
        if self.do_not_track is not None:
            base_dict['navigator'] = {'doNotTrack': self.do_not_track}
        if self.geolocation is not None:
            base_dict['geolocation'] = {'mode': self.geolocation}
        if self.hardware_canvas is not None:
            base_dict['canvas'] = {'mode': self.hardware_canvas}
        if self.local_storage is not None:
            base_dict['storage'] = {'local': self.local_storage}
        if self.service_worker_cache is not None:
            base_dict['storage'] = {
                'serviceWorkerCache': self.service_worker_cache}

        return base_dict


if __name__ == '__main__':
    profile_base = Profile()

    with open('resources/examples/example_profile.json', 'w') as file:
        json.dump(profile_base.as_dict(), file, indent='  ')

    profile_full = Profile(language="en-us;q=0.6, en-uk;q=0.3, it;q=0.1",
                           geolocation='ALLOW',
                           do_not_track=0,
                           hardware_canvas='NOISE',
                           local_storage=True,
                           service_worker_cache=True)
    with open('resources/examples/example_profile.json', 'w') as file:
        json.dump(profile_full.as_dict(), file, indent='  ')
