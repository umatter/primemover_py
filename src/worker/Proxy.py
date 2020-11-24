from src.worker.Info import ProxyInfo
import json
with open('resources/other/keys.json', 'r') as key_file:
    keys = json.load(key_file)
GEOSURF_USERNAME = keys['GEOSURF']['username']
GEOSURF_PASSWORD = keys['GEOSURF']['password']


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

    def as_dict(self):
        return_dict = {"name": self._name,
                       "description": self._description,
                       "type": self._type,
                       "hostname": self._hostname,
                       "port": self._port,
                       "username": self._username,
                       "password": self._password}
        if self._info is not None:
            for key, value in self._info.as_dict().items():
                return_dict['key'] = value
        return return_dict

    @classmethod
    def from_dict(cls, proxy_dict):
        proxy_object = cls(name=proxy_dict.get('name'),
                           description=proxy_dict.get('description'),
                           username=proxy_dict.get('username'),
                           password=proxy_dict.get('password'),
                           type=proxy_dict.get('type'),
                           hostname=proxy_dict.get('hostname'),
                           port=proxy_dict.get('port'),
                           info=ProxyInfo.from_dict(proxy_dict))
        return proxy_object
