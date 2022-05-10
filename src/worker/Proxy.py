"""
Proxy Class
matches the proxy object on the primemover_api
TODO Secure passwords
"""

from src.worker.Info import ProxyInfo
import json
import pathlib
import pandas as pd
from src.worker.History import S3History

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


PROXYPATHS = ['/resources/proxies/rotating_proxies.csv',
              '/resources/proxies/private_proxies.csv']


class Proxy:

    def __init__(self,
                 username=None,
                 password=None,
                 name="Sample Proxy",
                 description="Proxy",
                 type="GEOSURF",
                 hostname="state.geosurf.io",
                 port=8000,
                 info=None
                 ):
        with open(PRIMEMOVER_PATH + '/resources/other/keys.json',
                  'r') as key_file:
            self._keys = json.load(key_file)

        self._name = name
        self._description = description
        self._type = type
        if self._type == 'HTTP':
            self._internal_type = self._name.split()[0].upper()
        else:
            self._internal_type = self._type
        self._hostname = hostname
        self._port = port
        self.username = username
        self.password = password
        self._info = info
        if self._info is not None:
            self._history = S3History(self)
        else:
            self._history = None

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, val):
        if val is not None:
            self._password = val
        elif val is None and self._internal_type in ['GEOSURF', 'ROTATING', 'PRIVATE']:
            self._password = self._keys[self._internal_type]['password']
        else:
            self._password = ""

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, val):
        if val is not None:
            self._username = val
        elif val is None and self._internal_type in ['GEOSURF', 'ROTATING', 'PRIVATE']:
            self._username = self._keys[self._internal_type]['username']
        else:
            self._username = ""



    def _check_location_non_geosurf(self):
        """
        type: private
        params: self
        Updates location for non geosurf proxies, when a proxy is changed.
        Allways call after update_proxy
        """
        for path in PROXYPATHS:
            proxies = pd.read_csv(PRIMEMOVER_PATH + path)
            proxies['gateway_ip_port'] = proxies[
                'gateway_ip_port'].astype(str)
            proxies = proxies.loc[proxies['active'] == 1]
            proxies = proxies.loc[proxies['gateway_ip'] == self._hostname]
            proxies = proxies.loc[proxies['gateway_ip_port'] == self._port]

            if len(proxies) >= 1:
                return proxies.iloc[0]['loc_id']
        raise LookupError(
            'Cant match the hostname and port in the existing proxy files. Check if these are up to date_time.')

    def update_proxy(self, update_dict):
        """
        input: update_dict, keys <hostname>:<port>, value  <hostname>:<port>
        input dict, assigns new proxies to existing ones. If change occours,
        _check_location_nong_geosurf is called.
        """
        existing = f'{self._hostname}:{self._port}'
        new_proxy = update_dict.get(existing)
        if new_proxy is not None:
            self._history.pull_existing()
            self._hostname = new_proxy['host']
            self._port = new_proxy['port']
            self._history.update_current_status()
            self._history.push()
            return self._check_location_non_geosurf()
        else:
            return 'not updated'

    @property
    def info(self):
        return self._info

    def as_dict(self, send_info=False):
        return_dict = {"name": self._name,
                       "description": self._description,
                       "type": self._type,
                       "hostname": self._hostname,
                       "port": self._port,
                       "username": self.username,
                       "password": self.password}
        if send_info and self._info is not None:
            for key, value in self._info.as_dict().items():
                return_dict[key] = value
        return return_dict

    @classmethod
    def from_dict(cls, proxy_dict):
        if type(proxy_dict) is list:
            proxy_dict = proxy_dict[0]
        proxy_object = cls(name=proxy_dict.get('name'),
                           description=proxy_dict.get('description'),
                           # username=proxy_dict.get('username'),
                           # password=proxy_dict.get('password'),
                           type=proxy_dict.get('type'),
                           hostname=proxy_dict.get('hostname'),
                           port=proxy_dict.get('port'),
                           info=ProxyInfo.from_dict(proxy_dict))
        return proxy_object
