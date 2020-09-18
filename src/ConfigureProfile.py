import src.Preferences
import src.ConfigurationFunctions as C
import os
import pandas as pd


class Config:
    MEDIA_DEFAULT_PATH = None
    TERM_DEFAULT_PATH = None

    def __init__(self,
                 path_media_outlets=None,
                 path_terms=None,
                 psi=None,
                 pi=None,
                 alpha=None,
                 tau=None,
                 beta=None,
                 kappa=None,
                 media=None,
                 terms=None
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
            self._pi = C.Pi()
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
            raise ValueError(f'No such file exists {path}')

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
            raise ValueError(f'No such file exists {path}')

    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, media_list):
        if media_list is None:
            all_media_tbl = pd.read_csv(self.path_media_outlets, header=0,
                                        usecols=['redirect_url', 'pi', 'avg_reach_permillion'])
            all_media_tbl.rename(columns={'redirect_url': 'url', 'pi': 'pi', 'avg_reach_permillion': 'e^ro'},
                                 inplace=True)

            self._media = C.SelectMediaOutlets(pi_i=self.pi,
                                               url_pi_tbl=all_media_tbl,
                                               tau_tilde_ij=self.tau,
                                               k=10)

        elif type(media_list) is list and len(media_list) > 0:
            self._media = media_list
        else:
            raise TypeError(
                f'Media should be a list type object containing unique identifiers of online media outlets')

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, term_list):
        if term_list is None:
            all_terms_tbl = pd.read_csv(self.path_terms, header=0,
                                        usecols=['search_term', 'pi_p'])
            self._terms = C.SelectSearchTerms(term_pi_tbl=all_terms_tbl, k=30,
                                              pi_i=self._pi, tau_hat_ik=self.tau, alpha_hat=self.alpha)
        elif type(term_list) is list and len(term_list) > 0:
            self._terms = term_list
        else:
            raise TypeError(
                f'terms should be a list type object containing search terms')

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, val):
        self._location = val

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
        return {
            "name": "",
            "description": "",
            "params": {
                "pi": self.pi,
                "psi": self.psi,
                "alpha": self.alpha,
                "tau": self.tau,
                "kappa": self.kappa,
                "beta": self.beta,
                "search_terms": self.terms,
                "media_outlet_urls": self.media}}

    def update_config(self, results):
        """
        (if psi >0)
        :param results:
        :return:
        """


if __name__ == "__main__":
    trial_config = Config(
        path_media_outlets="/Users/johannes/Dropbox/websearch_polarization/data/final/outlets_pool.csv",
        path_terms="/Users/johannes/Dropbox/websearch_polarization/data/final/searchterms_pool.csv")
    print(trial_config.__str__())
