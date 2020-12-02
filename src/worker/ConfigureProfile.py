"""
Establishes the Config class, mirroring the configurations object in the primemover api
any parameters that are not set upon init are generated according to the
ConfigurationFunctions file.

J.L. 11.2020
"""

from src import ConfigurationFunctions
from src.worker.Info import ConfigurationInfo
import json
import os

resource_path = os


class Config:
    """A configuration object, sets all parameters documented in configurations.
    Most are standard, though these can be extended through optional parameters.
    In case this is required, extend the class.

    Public attributes:
         - name: string, optional but recomended, can be used to store information for processing
            use some_name/flag to add a flag to the configuration object.
            (It is part of the name attribute, to ensure availability on api return)
         - description: string, optional
         - psi: float in [0,1], individuals persuadability
            default: set according to ConfigurationFunctions
         - pi: float political orientation of individual
            default: set according to ConfigurationFunctions
         - alpha: float >= 0, shift parameter in media outlet utility
            default: set according to ConfigurationFunctions
         - tau: float > 0, "transportation costs" i.e. costs of consuming
                ideologically distant news outlets
            default: set according to ConfigurationFunctions
         - beta:
            default: set according to ConfigurationFunctions
         - kappa: binary in {0,1}, indicates whether individual can be persuaded
            default: set according to ConfigurationFunctions
         - media: list or dict, media redirect urls for outlets known to individual
            must be compatible with any tasks the user intends to set!
            default: set according to ConfigurationFunctions
         - terms: list or dict, search terms individual may search
            must be compatible with any tasks the user intends to set!
            default: set according to ConfigurationFunctions
         - location: string, must be in "resources/other/geosurf_cities.json"
            this is required for geosurf compatibility, restriction may be altered
            in future release
            default: set according to ConfigurationFunctions
    Private attributes:
        - info: should only be set using existing crawlers, via from_dict method.
    """

    with open("resources/other/geosurf_cities.json", 'r') as file:
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
                 info=None,
                 ):

        self.name = name
        self.description = description
        self._info = info
        if '/' in self.name:
            self._flag = self.name.split('/')[1]
        else:
            self._flag = None

        self.psi = psi
        self.pi = pi
        self.alpha = alpha
        self.tau = tau

        self.beta = beta
        self.kappa = kappa
        self.media = media
        self.terms = terms
        self.location = location

    @property
    def flag(self):
        return self._flag

    @property
    def psi(self):
        return self._psi

    @psi.setter
    def psi(self, value):
        if value is None:
            self._psi = ConfigurationFunctions.Psi()
        else:
            self._psi = float(value)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        if value is None:
            self._alpha = ConfigurationFunctions.alpha()
        else:
            self._alpha = float(value)

    @property
    def tau(self):
        return self._tau

    @tau.setter
    def tau(self, value):
        if value is None:
            self._tau = ConfigurationFunctions.tau()
        else:
            self._tau = float(value)

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        if value is None:
            self._beta = ConfigurationFunctions.beta()
        else:
            self._beta = float(value)

    @property
    def kappa(self):
        return self._kappa

    @kappa.setter
    def kappa(self, value):
        if value is None:
            self._kappa = ConfigurationFunctions.kappa()
        else:
            self._kappa = float(value)

    @property
    def pi(self):
        return self._pi

    @pi.setter
    def pi(self, value):
        if value is None:
            self._pi = ConfigurationFunctions.Pi(self._flag)
        else:
            self._pi = float(value)

    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, media_in):
        if media_in is None:
            self._media = ConfigurationFunctions.SelectMediaOutlets(pi=self._pi)
        elif type(media_in) in {list, dict}:
            self._media = media_in
        elif media_in == "":
            self._media = ""
        else:
            raise TypeError(
                f'Media should be a list type object containing unique identifiers of online media outlets')

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, term_dict):
        if term_dict is None:
            self._terms = ConfigurationFunctions.SelectSearchTerms(pi=self._pi)

        elif type(term_dict) is list:
            self._terms = term_dict
        elif type(term_dict) is dict:
            self._terms = term_dict
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
            self._location = ConfigurationFunctions.location()
        elif val in Config.LOCATION_LIST:
            self._location = val
        else:
            raise ValueError(
                f'{val} is not a valid location see geosurf cities')

    def as_dict(self):
        """
        Generate dictionary object from self, matching configurations in primemover api
        Returns: dict, valid configurations dictionary.
        """
        return_dict = {
            "name": self.name,
            "description": self.description,
            "params": [{
                "pi": self.pi,
                "psi": self.psi,
                "alpha": self.alpha,
                "tau": self.tau,
                "kappa": self.kappa,
                "beta": self.beta,
                "search_terms": self.terms,
                "media_outlet_urls": self.media}]
        }
        if self._info is not None:
            for key, value in self._info.as_dict().items():
                return_dict['key'] = value
            return_dict['params'][0]['user_id'] = self._info.as_dict()[
                'user_id']
            return_dict['params'][0]['configuration_id'] = self._info.as_dict()[
                'id']

        return return_dict

    def update_config(self, results):
        """
        Update self according to results
        """

    @classmethod
    def from_dict(cls, config_dict):
        """
        Generate config object from single api return
        Parameters:
            config_dict: api return of configurations. Note: media and terms
            must be json type objects!
        """
        config_object = cls(name=config_dict.get('name'),
                            description=config_dict.get('description'),
                            psi=config_dict['params'][0].get('psi'),
                            pi=config_dict['params'][0].get('pi'),
                            alpha=config_dict['params'][0].get('alpha'),
                            tau=config_dict['params'][0].get('tau'),
                            beta=config_dict['params'][0].get('beta'),
                            kappa=config_dict['params'][0].get('kappa'),
                            media=json.loads(config_dict['params'][0].get(
                                'media_outlet_urls')),
                            terms=json.loads(
                                config_dict['params'][0].get('search_terms')),
                            location=config_dict['params'][0].get('location'),
                            info=ConfigurationInfo.from_dict(config_dict)
                            )
        return config_object
