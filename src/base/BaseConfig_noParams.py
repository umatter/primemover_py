"""
Establishes the BaseConfig class, mirroring the configurations object in the primemover api
any parameters that are not set upon init are generated according to the
configuration_functions file.

J.L. 11.2020

Updated: Atharwa Deshmukh 05.2023
"""

from datetime import datetime
from src.base import base_config_functions
from src.worker.info import ConfigurationInfo
import json
import pathlib
from src.base.history import S3History
from src.worker.utilities import pref_as_dict

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


class BaseConfig_noParams:
    """A configuration object, sets all parameters documented in configurations.
    Most are standard, though these can be extended through optional parameters.
    In case this is required, extend the class.

    Public attributes:
         - name: string, optional but recommended, can be used to store information for processing
            use some_name/flag to add a flag to the configuration object.
            (It is part of the name attribute, to ensure availability on api return)
         - description: string, optional
         - psi: float in [0,1], individuals persuadability
            default: set according to CONFIGURATION_FUNCTIONS
         - pi: float political orientation of individual
            default: set according to CONFIGURATION_FUNCTIONS
         - alpha: float >= 0, shift parameter in media outlet utility
            default: set according to CONFIGURATION_FUNCTIONS
         - tau: float > 0, "transportation costs" i.e. costs of consuming
                ideologically distant news outlets
            default: set according to CONFIGURATION_FUNCTIONS
         - beta:
            default: set according to CONFIGURATION_FUNCTIONS
         - kappa: binary in {0,1}, indicates whether individual can be persuaded
            default: set according to CONFIGURATION_FUNCTIONS
         - media: list or dict, media redirect urls for outlets known to individual
            must be compatible with any tasks the user intends to set!
            default: set according to CONFIGURATION_FUNCTIONS
         - terms: list or dict, search terms individual may search
            must be compatible with any tasks the user intends to set!
            default: set according to CONFIGURATION_FUNCTIONS
         - location: string, must be in "resources/other/geosurf_cities.json"
            this is required for geosurf compatibility, restriction may be altered
            in future release
            default: set according to CONFIGURATION_FUNCTIONS
         - flag: contains some lable for the config objwct, will be identical to that of the crawler.
    Private attributes:
        - info: should only be set using existing crawlers, via from_dict method.
    """

    CONFIGURATION_FUNCTIONS = base_config_functions

    with open(PRIMEMOVER_PATH + "/resources/input_data/valid_cities.json",
              'r') as file:
        LOCATION_LIST = list(json.load(file).keys())

    def __init__(self,
                 name=None,
                 description=None,
                 psi=None,
                 pi=None,
                 alpha=None,
                 tau=None,
                 beta=None,
                 kappa=None,
                 media=None,
                 terms=None,
                 location=None,
                 cookie_pref=None,
                 info=None,
                 flag=None,
                 date_time=datetime.now()
                 ):

        self.name = name
        self.description = description
        self._info = info
        self.flag = flag

        self.psi = psi
        self.pi = pi
        self.alpha = alpha
        self.tau = tau

        self.beta = beta
        self.kappa = kappa

        self._state = None
        self.location = location

        self.media = media
        self.terms = terms
        self._date_time = date_time
        self.cookie_pref = cookie_pref
        if self.info is not None:
            self._history = S3History(self, date_time)
        else:
            self._history = None

    @property
    def info(self):
        return self._info

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        val = str(val)
        self._name = val

    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, val):
        if (val is None) and (self.name is not None) and ('/' in self.name):
            self._flag = self.name.split('/')[1]
        else:
            self._flag = val


    @property
    def psi(self):
        return self._psi

    @psi.setter
    def psi(self, value):
        if value is None:
             self._psi = []
        else:
            self._psi = float(value)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        if value is None:
            self._alpha = []
        else:
            self._alpha = float(value)

    @property
    def tau(self):
        return self._tau

    @tau.setter
    def tau(self, value):
        if value is None:
            self._tau = []
        else:
            self._tau = float(value)

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        if value is None:
            self._beta = []
        else:
            self._beta = float(value)

    @property
    def kappa(self):
        return self._kappa

    @kappa.setter
    def kappa(self, value):
        if value is None:
            self._kappa = []
        else:
            self._kappa = int(value)

    @property
    def pi(self):
        return self._pi

    @pi.setter
    def pi(self, value):
        self._pi = []
        

    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, media_in):
        if media_in is None:
            self._media = self.CONFIGURATION_FUNCTIONS.SelectMediaOutlets()
        elif type(media_in) in {list, dict}:
            self._media = media_in
        elif type(media_in) is str and media_in != "":
            self._media = json.loads(media_in)
        elif media_in == "":
            self._media = ""
        else:
            raise TypeError(
                f'Media should be a list job_type object containing unique identifiers of online media outlets')

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, term_dict):
        if term_dict is None:
            self._terms = self.CONFIGURATION_FUNCTIONS.SelectSearchTerms()

        elif type(term_dict) is list:
            self._terms = term_dict
        elif type(term_dict) is dict:
            self._terms = term_dict
        elif type(term_dict) is str and term_dict != "":
            self._terms = json.loads(term_dict)
        elif term_dict == "":
            self._terms = ""
        else:
            raise TypeError(
                f'terms should be a dict type object containing search terms')

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, val):
        if val is None:
            self._location = self.CONFIGURATION_FUNCTIONS.location()
        elif val.strip() in self.LOCATION_LIST:
            self._location = val.strip()
        else:
            raise ValueError(
                f'{val} is not a valid location see geosurf cities')
        segments = self._location.split('-')
        if type(segments) is list and len(segments) == 3:
            self._state = segments[0] + '-' + segments[1]
        else:
            self._state = None

    @property
    def history(self):
        return self._history

    @property
    def cookie_pref(self):
        return self._cookie_pref

    @cookie_pref.setter
    def cookie_pref(self, val):
        if (val is None) or (val == "Value not provided at update!"):
            val = self.CONFIGURATION_FUNCTIONS.cookie_pref()
        elif type(val) is str:
            try:
                val = json.loads(val)
            except:
                raise TypeError(
                    'cookie preferences should be a dictionary or at the very least a json containing "accept_all')

        if type(val) is dict and 'accept_all' in val.keys():
            self._cookie_pref = val
        else:
            raise ValueError('Not a valid value for cookie_pref')

    def as_dict(self, send_info=False):
        """
        Generate dictionary object from self, matching configurations in primemover api
        Returns: dict, valid configurations dictionary.
        """
        return_dict = {
            "name": self.name,
            "description": self.description,
            "params": [{
                "pi": [],
                "psi": self.psi,
                "alpha": self.alpha,
                "tau": self.tau,
                "kappa": self.kappa,
                "beta": self.beta,
                "search_terms": self.terms,
                "media_outlet_urls": self.media
            }],
            "preferences": [{
                "name": 'location',
                "value": self.location
            },
                {"name": "cookie_pref",
                 "value": json.dumps(self.cookie_pref)
                 },
                {"name": "flag",
                 "value": self.flag}
            ]
        }
        if send_info and self._info is not None:
            for key, value in self._info.as_dict().items():
                return_dict[key] = value
        # if self.history is not None and len(self.history.history) != 0:
        #     return_dict["preferences"].append({"name": "history",
        #                                        "value": str(list(
        #                                            self.history.history.keys()))})
        return return_dict

    def update_config(self, results, new_location):
        """
        Update self according to results
        """
        if self.info is not None:
            self.history.pull_existing()

        if new_location is not None:
            self.location = new_location
        # if results is not None and len(results) > 0:
        # do something
        self.history.update_current_status()
        self.history.push()

    @classmethod
    def from_dict(cls, config_dict, location, date_time=datetime.now()):
        """
        Generate config object from single api return
        Parameters:
            config_dict: api return of configurations. Note: media and terms
            must be json type objects!
        """
        if type(config_dict) is list:
            config_dict = config_dict[0]
        pref = pref_as_dict(config_dict.get('preferences', []))
        if ('location' in pref.keys()) and (location is not None):
            pref['location'] = location

        config_object = cls(name=config_dict.get('name'),
                            description=config_dict.get('description'),
                            psi=config_dict['params'][0].get('psi'),
                            pi=config_dict['params'][0].get('pi'),
                            alpha=config_dict['params'][0].get('alpha'),
                            tau=config_dict['params'][0].get('tau'),
                            beta=config_dict['params'][0].get('beta'),
                            kappa=config_dict['params'][0].get('kappa'),
                            media=config_dict['params'][0].get(
                                'media_outlet_urls'),
                            terms=config_dict['params'][0].get('search_terms'),
                            info=ConfigurationInfo.from_dict(config_dict),
                            date_time=date_time,
                            **pref
                            )
        return config_object
