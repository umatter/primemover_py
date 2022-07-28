"""
Profile defines the profile class, this mirrors the setup for multilogin.
J.L. - 11/2020
"""

from webob import acceptparse
import json
import warnings
import re
import pathlib
from src.base import base_config_functions
import random

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


class BaseProfile:
    CONFIGURATION_FUNCTIONS = base_config_functions

    def __init__(self,
                 name="%%AGENTID%%",
                 os='win',
                 browser='mimic',
                 language="PyDefault",
                 resolution='MultiloginDefault',
                 geolocation='PyDefault',
                 do_not_track='PyDefault',
                 hardware_canvas='PyDefault',
                 local_storage='PyDefault',
                 service_worker_cache='MultiloginDefault',
                 user_agent='MultiloginDefault',
                 platform='MultiloginDefault',
                 hardware_concurrency='MultiloginDefault',
                 base_dict=None
                 ):
        """
        ArgumentsTo
            - name: some string, defaults to placeholder for agent_id
            - os:  an os, must be in {'win', 'mac', 'linux', 'android'}
            - browser: must be in {'mimic', 'stealthfox', 'mimic_mobile'}
                mimic_mobile is only available when os is 'android'
            - language: string containing language and if desired preference for language
                e.g. 'en-US;q=0.8, it;q=0.1, fr-CA;q=0.1' (<language>-<region>;<preference>)
                only <language> is required e.g. ('en, it'). Websites should adjust according
                to these preferences. 'MultiloginDefault' will allow multilogin to set
            - geolocation: string in { PROMPT, BLOCK, ALLOW }, Note, Prompt is perhaps undesirable
                since it requires additional browser automation to accept. 'MultiloginDefault' will allow multilogin to set (default: 'MultiloginDefault')
            - do_not_track: 1,0 if 1, doNotTrack is on, else off. 'MultiloginDefault' will allow multilogin to set
            - hardware_canvas: one of [ REAL, BLOCK, NOISE ]. 'MultiloginDefault' will allow multilogin to set
            - local_storage: boolean, default:'MultiloginDefault' will allow multilogin to set. If local_storage is False, service_worker_cache is set to False
            - service_worker_cache: boolean, default: 'MultiloginDefault' will allow multilogin to set. If local_storage is False, service_worker_cache can not be set to True
        """

        self.os = os
        self.name = name
        self._browser = browser

        privacy_setting = False
        if privacy_setting:
            option = random.choice(
                ['geolocation', 'do_not_track', 'hardware_canvas',
                 'local_storage'])
        else:
            option = 'None'
        if language == 'PyDefault':
            self.language = self.CONFIGURATION_FUNCTIONS.language()
        else:
            self.language = language
        self._fill_based_on_external_ip = None
        if geolocation == 'PyDefault':
            self.geolocation = self.CONFIGURATION_FUNCTIONS.geolocation(option)
        else:
            self.geolocation = geolocation
        if do_not_track == 'PyDefault':
            self.do_not_track = self.CONFIGURATION_FUNCTIONS.do_not_track(option)
        else:
            self.do_not_track = do_not_track
        if hardware_canvas == 'PyDefault':
            self.hardware_canvas = self.CONFIGURATION_FUNCTIONS.hardware_canvas(option)
        else:
            self.hardware_canvas = hardware_canvas

        if local_storage == 'PyDefault':
            self.local_storage = self.CONFIGURATION_FUNCTIONS.local_storage(option)
        else:
            self.local_storage = local_storage

        self.hardware_concurrency = hardware_concurrency
        self.service_worker_cache = service_worker_cache
        self.resolution = resolution
        self.user_agent = user_agent
        self.platform = platform

        self.base_dict = base_dict

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
        if language_string == 'MultiloginDefault':
            self._language = None
        else:
            accept_header = acceptparse.create_accept_language_header(
                language_string)
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
            - string: desired setting {PROMPT, BLOCK, ALLOW, MultiloginDefault}
                MultiloginDefault -> NONE
        Exceptions:
            - ValueError: raises a value error when string is not a setting accepted by MultiLogin
        """
        string = string.strip().upper()
        valid_settings = {'PROMPT', 'BLOCK', 'ALLOW'}
        if string == 'MultiloginDefault':
            self._geolocation = None
        elif string in valid_settings:
            self._geolocation = string
            if string == 'ALLOW':
                self._fill_based_on_external_ip = True
            else:
                self._fill_based_on_external_ip = None
        else:
            self._fill_based_on_external_ip = None
            raise ValueError(
                f'geolocation must be one off {valid_settings}, received {string}')

    @property
    def do_not_track(self):
        return self._do_not_track

    @do_not_track.setter
    def do_not_track(self, value: int):
        if value == 'MultiloginDefault':
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
        if value == 'MultiloginDefault':
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
        if value == 'MultiloginDefault':
            self._service_worker_cache = None
        elif type(value) is str:
            value = value.strip().lower()
            if value == 'true':
                self._service_worker_cache = True
                if self._local_storage in {False, None}:
                    self._local_storage = True
                    warnings.warn(
                        'Attempting to set serviceWorkerCache True, while local storage is False or not set. This will be overwritten')

            elif value == 'false':
                # self._local_storage = False
                self._service_worker_cache = False
        elif value:
            self._service_worker_cache = value
            if self._local_storage in {False, None}:
                self._local_storage = True
                warnings.warn(
                    'Attempting to set serviceWorkerCache True, while local storage is False or not set. This will be overwritten')
        elif not value:
            # self._local_storage = False
            self._service_worker_cache = False
        else:
            raise ValueError('Invalid serviceWorkerCache value')

    @property
    def hardware_canvas(self):
        return self._hardware_canvas

    @hardware_canvas.setter
    def hardware_canvas(self, value):
        if value == 'MultiloginDefault':
            self._hardware_canvas = None
        else:
            value = value.strip().upper()
            if value in {'REAL', 'BLOCK', 'NOISE'}:
                self._hardware_canvas = value
            else:
                raise ValueError(
                    f'Invalid hardware_canvas setting, should be one of REAL,BLOCK, NOISE')

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, value):
        if value == 'MultiloginDefault':
            self._resolution = None
        elif re.fullmatch("^[0-9]+x[0-9]+", value.strip().lower()) is not None:
            value = value.strip().lower()
            self._resolution = value
        else:
            raise ValueError(
                f'Invalid hardware_canvas setting, should be one of REAL,BLOCK, NOISE')

    @property
    def base_dict(self):
        return self._base_dict

    @base_dict.setter
    def base_dict(self, val):

        if type(val) is dict and len(
                {'name', 'os', 'browser', 'network'}.intersection(val)) == 4:

            val['network']['proxy'] = {
                "type": "%%PROXYTYPE%%",
                "host": "%%PROXYHOST%%",
                "port": "%%PROXYPORT%%",
                "username": "%%PROXYUSERNAME%%",
                "password": "%%PROXYPASSWORD%%"
            }
            val['network']['dns'] = []

            self._base_dict = val
        else:
            self._base_dict = {
                "name": self.name,
                "os": self.os,
                "browser": self.browser,
                "network": {
                    "proxy": {
                        "type": "%%PROXYTYPE%%",
                        "host": "%%PROXYHOST%%",
                        "port": "%%PROXYPORT%%",
                        "username": "%%PROXYUSERNAME%%",
                        "password": "%%PROXYPASSWORD%%"
                    },
                    "dns": []
                }
            }

    def as_dict(self):
        base_dict = self.base_dict
        navigator = not (
                self.language is None and self.do_not_track is None and self.user_agent is None and self.hardware_concurrency is None and self.platform is None)
        if navigator:
            base_dict['navigator'] = {}
            if self.language not in [None, 'MultiloginDefault']:
                base_dict['navigator']['language'] = self.language
            if self.do_not_track not in [None, 'MultiloginDefault']:
                base_dict['navigator']['doNotTrack'] = self.do_not_track
            if self.user_agent not in [None, 'MultiloginDefault']:
                base_dict['navigator']['user_agent'] = self.user_agent
            if self.hardware_concurrency not in [None, 'MultiloginDefault']:
                base_dict['navigator'][
                    'hardware_concurrency'] = self.hardware_concurrency
            if self.platform not in [None, 'MultiloginDefault']:
                base_dict['navigator']['platform'] = self.platform

        if self.geolocation not in [None, 'MultiloginDefault']:
            base_dict['geolocation'] = {'mode': self.geolocation}
        if self._fill_based_on_external_ip not in [None, 'MultiloginDefault']:
            base_dict['geolocation'][
                'fillBasedOnExternalIp'] = self._fill_based_on_external_ip
        if self.hardware_canvas not in [None, 'MultiloginDefault']:
            base_dict['canvas'] = {'mode': self.hardware_canvas}
        if self.local_storage not in [None, 'MultiloginDefault']:
            base_dict['storage'] = {'local': self.local_storage}
        # if self.service_worker_cache not in [None, 'MultiloginDefault']:
        #     if 'storage' in base_dict:
        #         base_dict['storage'][
        #             'serviceWorkerCache'] = self.service_worker_cache
        #     else:
        #         base_dict['storage'] = {
        #             'serviceWorkerCache': self.service_worker_cache}

        return base_dict

    @classmethod
    def from_dict(cls, profile_dict: dict):
        navigator = profile_dict.get('navigator', {})

        profile_object = cls(
            name=profile_dict.get('name', "%%AGENTID%%"),
            os=profile_dict.get('os', 'win'),
            browser=profile_dict.get('browser', 'mimic'),
            language=navigator.get('language',
                                   "PyDefault"),
            # UPDATE Once Resolution is fully implemented
            resolution='MultiloginDefault',

            geolocation=profile_dict.get('geolocation', {}).get('mode',
                                                                "PyDefault"),
            do_not_track=navigator.get('doNotTrack',
                                       "PyDefault"),
            hardware_canvas=profile_dict.get('canvas', {}).get('mode',
                                                               "PyDefault"),
            local_storage=profile_dict.get('storage', {}).get('local',
                                                              "PyDefault"),
            service_worker_cache=profile_dict.get('storage', {}).get(
                'serviceWorkerCache', 'MultiloginDefault'),
            user_agent=navigator.get('user_agent', 'MultiloginDefault'),
            platform=navigator.get('platform', 'MultiloginDefault'),
            hardware_concurrency=navigator.get('hardware_concurrency',
                                               'MultiloginDefault'),
            base_dict=profile_dict
        )
        return profile_object


if __name__ == '__main__':
    profile_base = BaseProfile(language="en-us;q=1.0, en-uk;q=1.0, it;q=0.1",
                               geolocation='BLOCK',
                               do_not_track=1,
                               hardware_canvas='REAL',
                               local_storage=False,
                               service_worker_cache=True)

    with open(PRIMEMOVER_PATH + '/resources/examples/example_profile_0.json',
              'w') as file:
        json.dump(profile_base.as_dict(), file, indent='  ')
