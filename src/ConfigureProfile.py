import src.Preferences
from src.Info import *
import src.ConfigurationFunctions as C
import os
import pandas as pd


class Config:

    def __init__(self, path_media_outlets, path_terms, config_info=None,
                 psi=None, pi=None, media=None,
                 terms=None):
        self.config_info = config_info

        self.psi = psi
        self.pi = pi

        self.path_media_outlets = path_media_outlets
        self.path_terms = path_terms
        self.media = media
        self.terms = terms

    @property
    def config_info(self):
        return self._config_info

    @config_info.setter
    def config_info(self, info):
        if type(info) is not ConfigurationInfo:
            self._config_info = ConfigurationInfo()
        else:
            self._config_info = info

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
        if os.path.exists(path):
            self._path_media_outlets = path
        else:
            raise ValueError(f'No such file exists {path}')

    @property
    def path_terms(self):
        return self._path_terms

    @path_terms.setter
    def path_terms(self, path):
        if os.path.exists(path):
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
                                        usecols=['redirect_url', 'pi'])
            all_media_tbl.rename(columns={'redirect_url':'url', 'pi':'pi'}, inplace=True)
            self._media = C.SelectMediaOutlets(pi_i=self.pi,
                                               url_pi_tbl=all_media_tbl,
                                               n=100)

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
            self._terms = C.SelectSearchTerms(term_pi_tbl=all_terms_tbl, n=100,
                                              pi_i=self._pi)
        elif type(term_list) is list and len(term_list) > 0:
            self._terms = term_list
        else:
            raise TypeError(
                f'terms should be a list type object containing search terms')

    def __str__(self):

        config_discr = \
            f'"id": {self.config_info.configuration_id or ""},\n' \
            f'"user_id": "{self.config_info._user_id or ""}",\n' \
            f'"name": "",\n' \
            f'"description": "",\n' \
            f'"created_at":"{self._config_info.created_at or ""}",\n' \
            f'"updated_at":"{self._config_info.updated_at or ""}"'
        search_terms = '[\n"' + '",\n"'.join(self.terms) + '"\n]'
        media_outlets = '[\n"' + '",\n"'.join(self.media) + '"\n]'
        parameters = \
            f'"pi": {self.pi},\n' \
            f'"psi": {self.psi},\n' \
            f'"search_terms":{search_terms},\n'\
            f'"media_outlet_urls":{media_outlets}'

        return f'{{{config_discr},\n"parameters":{{\n{parameters}}}}}'

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
