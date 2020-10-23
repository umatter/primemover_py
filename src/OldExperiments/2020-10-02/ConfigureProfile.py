import src.OldExperiments.ConfigurationFunctions as C
from src.worker import api_wrapper
import os
import pandas as pd
from src.worker.Info import ConfigurationInfo
import json


class Config:
    MEDIA_DEFAULT_PATH = 'resources/input_data/outlets.json'
    TERM_DEFAULT_PATH = 'resources/input_data/terms.json'
    with open("resources/other/geosurf_cities.json", 'r') as file:
        LOCATION_LIST = list(json.load(file).keys())

    def __init__(self,
                 name=None,
                 description=None,
                 path_media_outlets="resources/input_data/outlets.json",
                 path_terms="resources/input_data/terms.json",
                 psi=None,
                 pi=None,
                 alpha=None,
                 tau=None,
                 lambd=None,
                 beta=None,
                 kappa=None,
                 media=None,
                 terms=None,
                 location=None,
                 info=None,
                 ):
        """
        :param path_media_outlets: path, csv containing media outlet data
        :param path_terms: path, csv containing search term data
        :param psi: float in [0,1], individuals persuadability
        :param pi: political orientation of individual
        :param alpha: float >= 0, shift parameter in media outlet utility
        :param tau:  float > 0, "transportation costs" i.e. costs of consuming
                ideologically distant news outlets
        :param beta:
        :param kappa: binary in {0,1}, indicates whether individual can be persuaded
        :param media: list, media redirect urls for outlets known to individual
        :param terms: list, search terms individual may search
        """
        self._name = name
        self._description = description
        self._info = info
        if '/' in self._name:
            self._flag = self._name.split('/')[1]
        else:
            self._flag = None

        self.psi = psi
        self.pi = pi
        self.alpha = alpha
        self.tau = tau

        self.beta = beta
        self.kappa = kappa
        self.path_media_outlets = path_media_outlets
        self.path_terms = path_terms
        self.media = media
        self.terms = terms
        self.location = location
        self._info = None

    @property
    def psi(self):
        return self._psi

    @psi.setter
    def psi(self, value):
        if value is None:
            self._psi = C.Psi()
        else:
            self._psi = float(value)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        if value is None:
            self._alpha = C.alpha()
        else:
            self._alpha = float(value)

    @property
    def tau(self):
        return self._tau

    @tau.setter
    def tau(self, value):
        if value is None:
            self._tau = C.tau()
        else:
            self._tau = float(value)

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        if value is None:
            self._beta = C.beta()
        else:
            self._beta = float(value)

    @property
    def kappa(self):
        return self._kappa

    @kappa.setter
    def kappa(self, value):
        if value is None:
            self._kappa = C.kappa()
        else:
            self._kappa = float(value)

    @property
    def pi(self):
        return self._pi

    @pi.setter
    def pi(self, value):
        if value is None:
            self._pi = C.Pi(self._flag)
        else:
            self._pi = float(value)

    @property
    def path_media_outlets(self):
        return self._path_media_outlets

    @path_media_outlets.setter
    def path_media_outlets(self, path):
        if path is None:
            if Config.MEDIA_DEFAULT_PATH is None:
                raise ValueError(
                    f'No media outlet path passed, with no default set')
            elif os.path.exists(Config.MEDIA_DEFAULT_PATH):
                self._path_media_outlets = Config.MEDIA_DEFAULT_PATH
            else:
                raise ValueError(
                    f'No media outlet path passed, with an invalid default')
        elif os.path.exists(path):
            self._path_media_outlets = path
        else:
            outlets = api_wrapper.get_outlets()
            with open(path, 'w') as file:
                json.dump(outlets, file, indent='  ')
            self._path_media_outlets = path

    @property
    def path_terms(self):
        return self._path_terms

    @path_terms.setter
    def path_terms(self, path):
        if path is None:
            if Config.TERM_DEFAULT_PATH is None:
                raise ValueError(
                    f'No terms outlet path passed, with no default set')
            elif os.path.exists(Config.TERM_DEFAULT_PATH):
                self._path_terms = Config.TERM_DEFAULT_PATH
            else:
                raise ValueError(
                    f'No terms outlet path passed, with an invalid default')
        elif os.path.exists(path):
            self._path_terms = path
        else:
            res = api_wrapper.get_terms()
            with open(path, 'w') as file:
                json.dump(res, file, indent='  ')
            self._path_terms = 'resources/input_data/terms.json'

    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, media_in):
        if media_in is None:
            # all_media_tbl = pd.read_csv(self.path_media_outlets, header=0,
            #             #                             usecols=['redirect_url', 'pi',
            #             #                                      'avg_reach_permillion'])
            with open(self.path_media_outlets, 'r') as file:
                all_media_tbl = pd.DataFrame.from_records(json.load(file),
                                                          columns=[
                                                              'redirect_url',
                                                              'pi',
                                                              'avg_reach_permillion',
                                                              'source'])
            all_media_tbl = \
            all_media_tbl.loc[all_media_tbl['source'] == 'gdelt_gfg'][[
                'redirect_url',
                'pi',
                'avg_reach_permillion']]
            all_media_tbl['pi'] = all_media_tbl['pi'].astype(float)
            all_media_tbl['avg_reach_permillion'] = all_media_tbl[
                'avg_reach_permillion'].astype(float)

            all_media_tbl.rename(columns={'redirect_url': 'url', 'pi': 'pi',
                                          'avg_reach_permillion': 'e^rho'},
                                 inplace=True)

            media_selection = C.SelectMediaOutlets(pi_i=self.pi,
                                                   alpha_tilde=self.alpha,
                                                   url_pi_tbl=all_media_tbl,
                                                   tau_tilde_ij=self.tau,
                                                   k=10)
            self._media = {}
            for url, pi, rho in media_selection:
                self._media[url] = {"pi": pi, "rho": rho}

        elif type(media_in) in {list, dict}:
            self._media = media_in
        else:
            raise TypeError(
                f'Media should be a list type object containing unique identifiers of online media outlets')

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, term_dict):
        if term_dict is None:
            # all_terms_tbl = pd.read_csv(self.path_terms, header=0,
            #                             usecols=['search_term', 'pi_p'])
            with open(self.path_terms, 'r') as file:
                all_terms_tbl = pd.DataFrame.from_records(json.load(file),
                                                          columns=[
                                                              'search_term',
                                                              'pi_p'])
            all_terms_tbl['pi_p'] = all_terms_tbl['pi_p'].astype(float)

            selected_terms = C.SelectSearchTerms(term_pi_tbl=all_terms_tbl,
                                                 k=30,
                                                 pi_i=self._pi,
                                                 tau_hat_ik=self.tau,
                                                 alpha_hat=self.alpha)
            self._terms = {}
            for term, pi in selected_terms:
                self._terms[term] = pi
        elif type(term_dict) is list:
            self._terms = term_dict
        elif type(term_dict) is dict:
            self._terms = term_dict
        else:
            raise TypeError(
                f'terms should be a dict type object containing search terms')

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, val):
        if val is None:
            self._location = C.location()
        elif val in Config.LOCATION_LIST:
            self._location = val
        else:
            raise ValueError(
                f'{val} is not a valid location see geosurf cities')

    def __str__(self):
        config_discr = \
            f'"name": "",\n' \
            f'"description": ""'
        search_terms = '[\n"' + '",\n"'.join(self.terms) + '"\n]'
        media_outlets = '[\n"' + '",\n"'.join(self.media) + '"\n]'
        parameters = \
            f'"pi": {self.pi},\n' \
            f'"psi": {self.psi},\n' \
            f'"search_terms":{search_terms},\n' \
            f'"media_outlet_urls":{media_outlets}'

        return f'{{{config_discr},\n"parameters":{{\n{parameters}}}}}'

    def as_dict(self):
        return_dict = {
            "name": self._name,
            "description": self._description,
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
        (if psi >0)
        :param results:
        :return:
        """

    @classmethod
    def from_dict(cls, config_dict):
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


if __name__ == "__main__":
    trial_config = Config(
        path_media_outlets="/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv",
        path_terms="/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv")
    print(trial_config.__str__())
