"""Use this file to define your own Tasks, as queue objects.
 Use help(Jobs) to see available job types.
 TODO re-structure tasks into a folder system for different tasks. Perhaps a base folder for reoccouring tasks and separate folders for different experiments.
 J.L. 03/2021
 """
from src.worker.PrimemoverQueue import Queue
from src.worker import Jobs
import random as r
import src.Preferences as Pref
from src.ConfigurationFunctions import NoiseUtility
import numpy as np
import json
import pathlib
import pandas as pd

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


class GoogleSearch(Queue):
    """
    Conduct a google search and scroll to the bottom of the page
    """

    def __init__(self,
                 term,
                 start_at,
                 name='GoogleSearch',
                 description='Open Google, enter a search querry and select a result.',
                 search_type='',
                 select_result=False
                 ):
        self._search_term = term
        super().__init__(start_at=start_at,
                         name=name,
                         description=description)
        # Add Job to Visit a webpage (google)
        self.jobs.append(
            Jobs.VisitJob(url='https://www.google.com', captcha_mode='always'))

        # Add Job to select the search field via XPATH and type the search term
        self.jobs.append(Jobs.EnterText(text=term,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS",
                                        flag=search_type,
                                        task=name,
                                        captcha_mode='always'),

                         )
        # Add Job to scroll to bottom
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=5,
                                     captcha_mode='always'))
        self.jobs.append(Jobs.Scroll(direction='UP',
                                     percentage=100,
                                     captcha_mode='always'))  # Add Job to select a result randomly
        if select_result:
            self.jobs.append(
                Jobs.SingleSelect(selector='.//div[@class="yuRUbf"]/a',
                                  selector_type='XPATH',
                                  decision_type="CALCULATED",
                                  flag=search_type,
                                  task=name,
                                  captcha_mode='always'
                                  )
            )

            # Add Job to scroll down 80% of the visited page
            self.jobs.append(Jobs.Scroll(direction='DOWN',
                                         percentage=80,
                                         captcha_mode='always'))


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
        self.jobs.append(
            Jobs.VisitJob(url='https://www.google.com', captcha_mode='always'))

        # Add Job to select the search field via XPATH and type the outlets name
        self.jobs.append(Jobs.EnterText(text=self._outlet_name,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        captcha_mode='always')
                         )
        # Add Job to wait for a random nr. of seconds
        self.jobs.append(Jobs.Wait(time=r.randint(1, 6),
                                   captcha_mode='always'
                                   )
                         )

        # Add Job to select the first result
        self.jobs.append(Jobs.SingleSelect(selector='.//div[@class="yuRUbf"]/a',
                                           selector_type='XPATH',
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

    def __init__(self, crawler, start_at, term_type=None):
        terms = crawler.configuration.terms
        if term_type is not None:
            terms = terms.get(term_type)
        pi_i = crawler.configuration.pi
        alpha_hat = crawler.configuration.alpha
        tau_hat_ik = crawler.configuration.tau

        utilities = []
        ordered_terms = []
        for term in terms:
            term_k = term.get('term')
            pi_hat_k = term.get('pi')
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
                         name='search_google_political',
                         search_type='political',
                         select_result=True)


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
        for outlet in media:
            url = outlet['url']
            pi_tilde_j = outlet['pi']
            epsilon_ik = NoiseUtility()
            utilities.append(Pref.media_utility_u_ij(pi_i=pi_i,
                                                     pi_tilde_j=pi_tilde_j,
                                                     epsilon_ij=epsilon_ik,
                                                     alpha_tilde=alpha_tilde,
                                                     tau_tilde_ij=tau_tilde_ij))
            ordered_outlets.append(url)

        probabilities = Pref.prob_i(utilities)

        i = np.random.multinomial(1, probabilities).argmax()

        url = ordered_outlets[i]

        super().__init__(outlet_url=url,
                         start_at=start_at)


class NeutralGoogleSearch(GoogleSearch):
    def __init__(self, term, start_at):
        super().__init__(term=term,
                         name='search_google_neutral',
                         start_at=start_at,
                         search_type='neutral',
                         select_result=True)


class BenignGoogleSearch(GoogleSearch):
    def __init__(self, term, start_at):
        super().__init__(term=term, name='search_google_benign',
                         start_at=start_at,
                         search_type='benign',
                         select_result=False)


class VisitFrequentDirect(VisitDirect):
    def __init__(self, start_at,
                 file_path=PRIMEMOVER_PATH + '/resources/other/most_visited.json'):
        with open(file_path, 'r') as file:
            urls = json.load(file)
        url = r.choice(urls)
        super().__init__(outlet_url=url, start_at=start_at)


class VisitNeutralDirect(VisitDirect):
    def __init__(self, start_at,
                 file_path='/resources/input_data/neutraldomains_pool.csv'):
        domains = pd.read_csv(PRIMEMOVER_PATH + file_path)
        url = r.choice(domains['redirect_url'])
        super().__init__(outlet_url=url, start_at=start_at)


class PoliticalSearchNoUtility(GoogleSearch):
    PASS_CRAWLER = True
    """
    Conduct a google political search and scroll to the bottom of the page
    """

    def __init__(self, crawler, start_at, term_type=None):
        terms = crawler.configuration.terms
        if term_type is not None:
            terms = terms.get(term_type)

        super().__init__(term=r.choice(terms),
                         start_at=start_at,
                         name='search_google_political_no_utility',
                         search_type='political_' + term_type,
                         select_result=True)


class VisitMediaNoUtility(VisitDirect):
    PASS_CRAWLER = True
    """
    Conduct a google political search and scroll to the bottom of the page
    """

    def __init__(self, crawler, start_at):
        media = crawler.configuration.media
        url = r.choice(list(media.values()))
        super().__init__(outlet_url=url,
                         start_at=start_at)


class VisitMediaGoogleNoUtility(GoogleSearch):
    PASS_CRAWLER = True
    """
    Conduct a google political search and scroll to the bottom of the page
    """

    def __init__(self, crawler, start_at):
        media = crawler.configuration.media
        domain = r.choice(list(media.keys()))
        super().__init__(term=domain,
                         start_at=start_at,
                         name='search_google_political_media_no_utility',
                         search_type='political_media',
                         select_result=True)


class BrowserLeaks(Queue):
    """
        Visit browserleaks.com and retrive all content
    """

    def __init__(self, start_at):
        super().__init__(start_at=start_at,
                         name='BrowserLeaks',
                         description='Visit a browserleaks.com and extract all data.')
        # IP site
        self.jobs.append(
            Jobs.VisitJob(url="https://browserleaks.com/ip", flag='leak_ip',
                          task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))

        # JavaScript
        self.jobs.append(
            Jobs.VisitJob(url="https://browserleaks.com/javascript",
                          flag='leak_javascript', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))

        # Webrtc
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/webrtc",
                                       flag='leak_webrtc', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))

        # Canvas
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/canvas",
                                       flag='leak_canvas', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))

        # Webgl
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/webgl",
                                       flag='leak_webgl', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))
        # Fonts
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/fonts",
                                       flag='leak_fonts', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))
        # SSL
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/ssl",
                                       flag='leak_ssl', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))
        # GeoLocation
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/geo",
                                       flag='leak_geo', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))
        # Features
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/features",
                                       flag='leak_features',
                                       task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))
        # Proxy
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/proxy",
                                       flag='leak_proxy', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))

        # Java system
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/java",
                                       flag='leak_java', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))

        # Flash
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/flash",
                                       flag='leak_flash', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))

        # Silverlight
        self.jobs.append(
            Jobs.VisitJob(url="https://browserleaks.com/silverlight",
                          flag='leak_silverlight', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(5, 10)))


class SetNrResults(Queue):
    PASS_CRAWLER = False
    """
    Visit Google and adjust the number of search results
    """

    def __init__(self, start_at, nr_results=50):
        super().__init__(start_at=start_at,
                         name='Set_Nr_Results',
                         )

        self.jobs.append(
            Jobs.VisitJob(url="https://www.google.com", task=self.name,
                          captcha_mode='always'))
        self.jobs.append(Jobs.TryClick(selector_type="XPATH",
                                       selector='//*[@id="Mses6b"]',
                                       task=self.name,
                                       captcha_mode='always'))

        self.jobs.append(Jobs.TryClick(selector_type="XPATH",
                                       selector='//*[@id="dEjpnf"]/li[1]',
                                       task=self.name,
                                       captcha_mode='always'))
        nr_results = round(nr_results, -1)
        click_dict = {10: (5, 1), 20: (4, 2), 30: (3, 3), 40: (3, 4),
                      50: (4, 5), 100: (5, 6)}

        if nr_results in click_dict.keys():
            position = click_dict[nr_results][1]
            nr_click = click_dict[nr_results][0]
            click_list = nr_click * [Jobs.TryClick(selector_type="XPATH",
                                                   selector=f'//*[@id="result_slider"]/ol/li[{position}]',
                                                   task=self.name,
                                                   captcha_mode='always')]

            self.jobs = self.jobs + click_list
        else:
            raise ValueError('Can only set 10,20,30,40,50 or 100 results')

        self.jobs.append(
            Jobs.Scroll(direction='DOWN', percentage=100, task=self.name,
                        captcha_mode='always'))

        self.jobs.append(Jobs.TryClick(selector_type="XPATH",
                                       selector='//*[@id="form-buttons"]/div[1]',
                                       task=self.name,
                                       captcha_mode='always'))
        self.jobs.append(Jobs.TryHandleAlertJob("ACCEPT", task=self.name,
                                                captcha_mode='always'))
