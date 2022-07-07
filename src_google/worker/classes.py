"""Re-Define base classes to make changes that render them usable for the Google Experiment"""

from src.base.BaseAgent import BaseAgent
from src.base.BaseProfile import BaseProfile
from src.base.BaseProxy import BaseProxy
from src.base.BaseConfig import BaseConfig
from src.base.BaseCrawler import BaseCrawler

from src.worker.info import ConfigurationInfo
from src.worker.TimeHandler import TimeHandler
from src.worker.utilities import pref_as_dict

from datetime import datetime
import json

from src_google.worker import config_functions, preferences


class Proxy(BaseProxy):
    """
    Re-define BaseProxy class. This particular re-definition does not alter the parent class and is hence redundant.
    I include it here for completeness. If you choose to omit this code, make sure to
    remove changes to the PROXY_CLASS variable.
    """
    def __init__(self,
                 username=None,
                 password=None,
                 name="Google Proxy",
                 description="Proxy",
                 type="GEOSURF",
                 hostname="state.geosurf.io",
                 port=8000,
                 info=None
                 ):
        super().__init__(username=username,
                         password=password,
                         name=name,
                         description=description,
                         type=type,
                         hostname=hostname,
                         port=port,
                         info=info
                         )


class Profile(BaseProfile):
    """
    Re-Define BaseProfile class. Note, it is essential to update the CONFIGURATION_FUNCTIONS
    constant.
    """
    # Change set of configuration functions to Google Specific setup
    CONFIGURATION_FUNCTIONS = config_functions

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
        super().__init__(name=name,
                         os=os,
                         browser=browser,
                         language=language,
                         resolution=resolution,
                         geolocation=geolocation,
                         do_not_track=do_not_track,
                         hardware_canvas=hardware_canvas,
                         local_storage=local_storage,
                         service_worker_cache=service_worker_cache,
                         user_agent=user_agent,
                         platform=platform,
                         hardware_concurrency=hardware_concurrency,
                         base_dict=base_dict)


class Agent(BaseAgent):
    """
    Re-define Base Agent. No changes in this instance. Can be omitted in which case
    AGENT_CLASS should not be re-defined in Crawler.
    """
    PROFILE_CLASS = Profile

    def __init__(self,
                 location=None,
                 name='Agent',
                 description='This is the agent',
                 identification="MultiLogin",
                 multilogin_id=None,
                 multilogin_profile=None,
                 info=None):
        super().__init__(location=location,
                         name=name,
                         description=description,
                         identification=identification,
                         multilogin_id=multilogin_id,
                         multilogin_profile=multilogin_profile,
                         info=info)


class Config(BaseConfig):
    """
    Re-define BaseConfig.
    """
    CONFIGURATION_FUNCTIONS = config_functions

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
                 usage_type=None,
                 cookie_pref=None,
                 info=None,
                 date_time=datetime.now()
                 ):
        self.usage_type = usage_type
        super().__init__(name=name,
                         description=description,
                         psi=psi,
                         pi=pi,
                         alpha=alpha,
                         tau=tau,
                         beta=beta,
                         kappa=kappa,
                         media=media,
                         terms=terms,
                         location=location,
                         cookie_pref=cookie_pref,
                         info=info,
                         date_time=date_time)

    @BaseConfig.media.setter
    def media(self, media_in):
        if media_in is None:
            self._media = self.CONFIGURATION_FUNCTIONS.SelectMediaOutlets(
                pi=self._pi,
                alpha_tilde=self.alpha,
                tau_tilde_ij=self.tau,
                k=8,
                local=2)
        elif type(media_in) in {list, dict}:
            self._media = media_in
        elif type(media_in) is str and media_in != "":
            self._media = json.loads(media_in)
        elif media_in == "":
            self._media = ""
        else:
            raise TypeError(
                f'Media should be a list job_type object containing unique identifiers of online media outlets')

    @BaseConfig.terms.setter
    def terms(self, term_dict):
        if term_dict is None:
            self._terms = self.CONFIGURATION_FUNCTIONS.SelectSearchTerms(
                pi=self.pi,
                alpha_hat=self.alpha,
                tau_hat_ik=self.tau,
                k=40)

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
                f'terms should be a dict job_type object containing search terms')

    @property
    def usage_type(self):
        return self._usage_type

    @usage_type.setter
    def usage_type(self, val):
        if (val is None) or (val == "Value not provided at update!"):
            val = self.CONFIGURATION_FUNCTIONS.usage_type()
        elif type(val) is str:
            val = val.lower().strip()
        if val in ['only_search', 'only_direct', 'both']:
            self._usage_type = val
        else:
            raise ValueError('Not a valid value for usage_type')

    def as_dict(self, send_info=False):
        base_dict = super().as_dict(send_info)
        usage_type_preference = {
            "name": 'usage_type',
            "value": self.usage_type
        }

        base_dict["preferences"].append(usage_type_preference)

        return base_dict

    def update_config(self, results, new_location, terms=True):

        """
        Update self according to results
        """
        if self.info is not None:
            self.history.pull_existing()

        if new_location is not None:
            self.location = new_location
        kappa_j_t = self.kappa
        if results is not None and len(results) > 0:
            pi_0 = self.pi
            for outlet in results:
                if 2 == self.kappa:
                    if not outlet['known']:
                        kappa_j_t = 1
                    else:
                        kappa_j_t = 0

                self.pi = preferences.political_orientation_pi_i_t(
                    psi_i=self.psi, kappa_j_t_prev=kappa_j_t,
                    pi_tilde_j_prev=outlet['pi'], pi_i_prev=self.pi)

            self.media = self.CONFIGURATION_FUNCTIONS.update_media_outlets(
                outlets=self.media + results, alpha_tilde=self.alpha,
                pi=self.pi,
                tau_tilde_ij=self.tau, k=10)
            if terms and pi_0 != self.pi:
                self.terms = self.CONFIGURATION_FUNCTIONS.SelectSearchTerms(
                    pi=self.pi,
                    alpha_hat=self.alpha,
                    tau_hat_ik=self.tau,
                    k=40)

        self.history.update_current_status()
        self.history.push()

    @classmethod
    def from_dict(cls, config_dict, location, date_time=datetime.now()):
        """
        Generate config object from single api return
        Parameters:
            config_dict: api return of configurations. Note: media and terms
            must be json job_type objects!
        """
        if type(config_dict) is list:
            config_dict = config_dict[0]
        pref = pref_as_dict(config_dict.get('preferences', []))
        usage_type = pref.get('usage_type', None)
        cookie_pref = pref.get('cookie_pref', None)
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
                            location=location,
                            date_time=date_time,
                            usage_type=usage_type,
                            cookie_pref=cookie_pref
                            )
        return config_object


class Crawler(BaseCrawler):
    CONFIG_CLASS = Config
    AGENT_CLASS = Agent
    PROXY_CLASS = Proxy

    def __init__(self,
                 name=None,
                 description="Crawler created through py",
                 configuration=None,
                 agent=None,
                 proxy=None,
                 active=1,
                 schedule=None,
                 testing=0,
                 crawler_info=None,
                 flag=None,
                 experiment_id=None,
                 date_time=datetime.now()
                 ):
        super().__init__(name=name,
                         description=description,
                         configuration=configuration,
                         agent=agent,
                         proxy=proxy,
                         active=active,
                         schedule=schedule,
                         testing=testing,
                         crawler_info=crawler_info,
                         flag=flag,
                         experiment_id=experiment_id,
                         date_time=date_time)

    @BaseCrawler.schedule.setter
    def schedule(self, val):
        if val is None:
            self._schedule = TimeHandler(self.agent.location,
                                         interval=120,
                                         wake_time=10 * 60 * 60,
                                         bed_time=17 * 60 * 60,
                                         date_time=self._date_time)
        else:
            self._schedule = val
