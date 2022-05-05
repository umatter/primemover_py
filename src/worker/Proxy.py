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

with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as key_file:
    keys = json.load(key_file)
GEOSURF_USERNAME = keys['GEOSURF']['username']
GEOSURF_PASSWORD = keys['GEOSURF']['password']

PROXYPATHS = ['/resources/proxies/rotating_proxies.csv',
              '/resources/proxies/private_proxies.csv']


class Proxy:

    def __init__(self,
                 username=GEOSURF_USERNAME,
                 password=GEOSURF_PASSWORD,
                 name="Sample Proxy",
                 description="Proxy",
                 type="GEOSURF",
                 hostname="state.geosurf.io",
                 port=8000,
                 info=None
                 ):
        self._name = name
        self._description = description
        self._type = type
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._info = info
        if self._info is not None:
            self._history = S3History(self)
        else:
            self._history = None

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
                       "username": self._username,
                       "password": self._password}
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
