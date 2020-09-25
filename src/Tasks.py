"""Use this file to define your own Tasks, as queue objects.
 Use help(Jobs) to see available job types."""
from src.worker.Queue import Queue
from src.worker import Jobs
import random as r
import src.Preferences as Pref
from src.ConfigurationFunctions import NoiseUtility
import numpy as np


class GoogleSearch(Queue):
    """
    Conduct a google search and scroll to the bottom of the page
    """

    def __init__(self, term, start_at, name='GoogleSearch',
                 description='Open Google, enter a search querry and select a result.'):
        self._search_term = term
        super().__init__(start_at=start_at,
                         name=name,
                         description=description)
        # Add Job to Visit a webpage (google)
        self.jobs.append(Jobs.VisitJob(url='https://www.google.com'))

        # Add Job to select the search field via XPATH and type the search term
        self.jobs.append(Jobs.EnterText(text=term,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS")
                         )
        # Add Job to select a result randomly
        self.jobs.append(Jobs.SingleSelect(selector="LC20lb.DKV0Md",
                                           selector_type='CLASS',
                                           decision_type="RANDOM"
                                           )
                         )

        # Add Job to scroll down 80% of the visited page
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     percentage=80))


class VisitDirect(Queue):
    """
        Visit a media outlet and scroll for 2-3 minutes
    """

    def __init__(self, outlet_url, start_at):
        self._outlet_url = outlet_url
        self._duration = r.randint(60, 180)  # choose scroll time in seconds
        super().__init__(start_at=start_at,
                         name='Visit Direct',
                         description='Visit a media outlet and scroll for 2-3 minutes.')
        # Add Job to Visit a media outlet
        self.jobs.append(Jobs.VisitJob(url=self._outlet_url))

        # Add Job to scroll down for random time between 1 and 3 minutes
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=self._duration))


class VisitViaGoogle(Queue):
    """
        Visit a media outlet and scroll for 2-3 minutes
    """

    def __init__(self, outlet_name, start_time):
        self._outlet_name = outlet_name
        self._duration = r.randint(60, 180)  # choose scroll time in seconds
        super().__init__(start_at=start_time,
                         name='Visit via Googe',
                         description='Visit a media outlet via google and scroll for some time.')
        # Add Job to Visit a  Google
        self.jobs.append(Jobs.VisitJob(url='https://www.google.com'))

        # Add Job to select the search field via XPATH and type the outlets name
        self.jobs.append(Jobs.EnterText(text=self._outlet_name,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH')
                         )
        # Add Job to wait for a random nr. of seconds
        self.jobs.append(Jobs.Wait(time=r.randint(1, 6)
                                   )
                         )

        # Add Job to select the first result
        self.jobs.append(Jobs.SingleSelect(selector="LC20lb.DKV0Md",
                                           selector_type='CLASS',
                                           decision_type="FIRST"
                                           )
                         )

        # Add Job to scroll down the visited page for some time
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=self._duration))


class PoliticalSearch(GoogleSearch):
    PASS_CRAWLER = True
    """
    Conduct a google political search and scroll to the bottom of the page
    """

    def __init__(self, crawler, start_at):
        terms = crawler.configuration.terms
        pi_i = crawler.configuration.pi
        alpha_hat = crawler.configuration.alpha
        tau_hat_ik = crawler.configuration.tau

        utilities = []
        ordered_terms = []
        for term_k, pi_hat_k in terms.items():
            epsilon_ik = NoiseUtility()
            utilities.append(Pref.search_utility_v_ik(
                pi_i=pi_i,
                pi_hat_k=pi_hat_k,
                epsilon_ik=epsilon_ik,
                alpha_hat=alpha_hat,
                tau_hat_ik=tau_hat_ik))
            ordered_terms.append(term_k)

        probabilities = Pref.prob_i(utilities)

        i = np.random.multinomial(1, probabilities).argmax()

        term = ordered_terms[i]

        super().__init__(term=term,
                         start_at=start_at,
                         name='search_google_political')


class VisitMedia(VisitDirect):
    PASS_CRAWLER = True
    """
    Conduct a google political search and scroll to the bottom of the page
    """

    def __init__(self, crawler, start_at):
        media = crawler.configuration.media
        pi_i = crawler.configuration.pi
        alpha_tilde = crawler.configuration.alpha
        tau_tilde_ij = crawler.configuration.tau

        utilities = []
        ordered_outlets = []
        for url, vals in media.items():
            pi_tilde_j = vals['pi']
            rho_j = vals['rho']
            epsilon_ik = NoiseUtility()
            utilities.append(Pref.media_utility_u_ij(pi_i=pi_i,
                                                     pi_tilde_j=pi_tilde_j,
                                                     epsilon_ij=epsilon_ik,
                                                     alpha_tilde=alpha_tilde,
                                                     rho_j=rho_j,
                                                     tau_tilde_ij=tau_tilde_ij))
            ordered_outlets.append(url)

        probabilities = Pref.prob_i(utilities)

        i = np.random.multinomial(1, probabilities).argmax()

        url = ordered_outlets[i]

        super().__init__(outlet_url=url,
                         start_at=start_at)
