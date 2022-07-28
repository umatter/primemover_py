"""Use this file to define your own Tasks, as queue objects.
 Use help(jobs) to see available job types.
 TODO re-structure tasks into a folder system for different tasks. Perhaps a base folder for reoccouring tasks and separate folders for different experiments.
 J.L. 03/2021
 """
from src.worker.PrimemoverQueue import Queue
from src.worker import jobs

from src.base.base_tasks import VisitDirect

import src_google.worker.preferences as pref
from src_google.worker.config_functions import NoiseUtility

import random as r

import numpy as np
import json
import pathlib
import pandas as pd

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


class GoogleSearchNew(Queue):
    """
    Conduct a google search and scroll to the bottom of the page
    """

    def __init__(self,
                 term,
                 start_at,
                 name='GoogleSearch',
                 description='Open Google, enter a search query and select a result.',
                 search_type='google_search',
                 select_result=False,
                 time_spent=5
                 ):
        self._search_term = term
        self._time_spent = time_spent
        self._search_type = search_type
        self._select_result = select_result
        super().__init__(start_at=start_at,
                         name=name,
                         description=description)
        # Add Job to Visit a webpage (google)
        self.jobs.append(
            jobs.VisitJob(url='https://www.google.com', captcha_mode='always',
                          task=name))

        # Add Job to select the search field via XPATH and job_type the search term
        self.jobs.append(jobs.EnterText(text=term,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS",
                                        task=name,
                                        captcha_mode='always'),

                         )
        # Add Job to scroll to bottom
        self.jobs.append(jobs.Scroll(direction='DOWN',
                                     percentage=100,
                                     captcha_mode='always', task=name))
        self.jobs.append(jobs.Scroll(direction='UP',
                                     percentage=100,
                                     captcha_mode='always',
                                     task=name,
                                     flag=self._search_type))  # Add Job to select a result randomly
        if self._select_result:
            self.jobs.append(
                jobs.SingleSelect_New(
                    click_selector='.//div[@class="yuRUbf"]/a',
                    click_selector_type='XPATH',
                    decision_type="CALCULATED",
                    criteria_extractor='^(?:https?\:\/\/)?(?:www.)?([^\/?#]+)(?:[\/?#]|$)',
                    flag=self._search_type,
                    task=name,
                    captcha_mode='always'
                )
            )

            # Add Job to scroll down 80% of the visited page
            self.jobs.append(jobs.Scroll(direction='DOWN',
                                         duration=self._time_spent,
                                         captcha_mode='always',
                                         task=name))


class GoogleSearch(Queue):
    """
    Conduct a google search and scroll to the bottom of the page
    """

    def __init__(self,
                 term,
                 start_at,
                 name='GoogleSearch',
                 description='Open Google, enter a search query and select a result.',
                 search_type='google_search',
                 select_result=False,
                 time_spent=5
                 ):
        self._search_term = term
        self._time_spent = time_spent
        self._select_result = select_result
        self._search_type = search_type
        super().__init__(start_at=start_at,
                         name=name,
                         description=description)
        # Add Job to Visit a webpage (google)
        self.jobs.append(
            jobs.VisitJob(url='https://www.google.com', captcha_mode='always',
                          task=name))

        # Add Job to select the search field via XPATH and type the search term
        self.jobs.append(jobs.EnterText(text=term,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS",
                                        task=name,
                                        captcha_mode='always'),

                         )
        # Add Job to scroll to bottom
        self.jobs.append(jobs.Scroll(direction='DOWN',
                                     percentage=100,
                                     captcha_mode='always', task=name))
        self.jobs.append(jobs.Scroll(direction='UP',
                                     percentage=100,
                                     captcha_mode='always',
                                     task=name,
                                     flag=self._search_type))  # Add Job to select a result randomly
        if self._select_result:
            self.jobs.append(
                jobs.SingleSelect(selector='.//div[@class="yuRUbf"]/a',
                                  selector_type='XPATH',
                                  decision_type="CALCULATED",
                                  flag=self._search_type,
                                  task=name,
                                  captcha_mode='always'
                                  )
            )

            # Add Job to scroll down 80% of the visited page
            self.jobs.append(jobs.Scroll(direction='DOWN',
                                         duration=self._time_spent,
                                         captcha_mode='always',
                                         task=name))


class VisitViaGoogle(Queue):
    """
        Visit a media outlet and scroll for 2-3 minutes
    """

    def __init__(self, outlet_name, start_time):
        self._outlet_name = outlet_name
        self._duration = r.randint(30, 60)  # choose scroll time in seconds
        super().__init__(start_at=start_time,
                         name='Visit via Googe',
                         description='Visit a media outlet via google and scroll for some time.', )
        # Add Job to Visit a  Google
        self.jobs.append(
            jobs.VisitJob(url='https://www.google.com', captcha_mode='always',
                          task=self.name))

        # Add Job to select the search field via XPATH and type the outlets name
        self.jobs.append(jobs.EnterText(text=self._outlet_name,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        captcha_mode='always',
                                        task=self.name)
                         )
        # Add Job to wait for a random nr. of seconds
        self.jobs.append(jobs.Wait(time=r.randint(1, 6),
                                   captcha_mode='always',
                                   task=self.name
                                   )
                         )

        # Add Job to select the first result
        self.jobs.append(jobs.SingleSelect(selector='.//div[@class="yuRUbf"]/a',
                                           selector_type='XPATH',
                                           decision_type="FIRST",
                                           task=self.name
                                           )
                         )

        # Add Job to scroll down the visited page for some time
        self.jobs.append(jobs.Scroll(direction='DOWN',
                                     duration=self._duration,
                                     task=self.name))


class VisitViaGoogleNew(Queue):
    """
        Visit a media outlet and scroll for 2-3 minutes
    """

    def __init__(self, outlet_name, start_time):
        self._outlet_name = outlet_name
        self._duration = r.randint(30, 60)  # choose scroll time in seconds
        super().__init__(start_at=start_time,
                         name='Visit via Googe',
                         description='Visit a media outlet via google and scroll for some time.', )
        # Add Job to Visit a  Google
        self.jobs.append(
            jobs.VisitJob(url='https://www.google.com', captcha_mode='always',
                          task=self.name))

        # Add Job to select the search field via XPATH and job_type the outlets name
        self.jobs.append(jobs.EnterText(text=self._outlet_name,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        captcha_mode='always',
                                        task=self.name)
                         )
        # Add Job to wait for a random nr. of seconds
        self.jobs.append(jobs.Wait(time=r.randint(1, 6),
                                   captcha_mode='always',
                                   task=self.name
                                   )
                         )

        # Add Job to select the first result

        self.jobs.append(
            jobs.SingleSelect_New(click_selector='.//div[@class="yuRUbf"]/a',
                                  click_selector_type='XPATH',
                                  decision_type="FIRST",
                                  task=self.name)
        )

        # Add Job to scroll down the visited page for some time
        self.jobs.append(jobs.Scroll(direction='DOWN',
                                     duration=self._duration,
                                     task=self.name))


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
            utilities.append(pref.search_utility_v_ik(
                pi_i=pi_i,
                pi_hat_k=pi_hat_k,
                epsilon_ik=epsilon_ik,
                alpha_hat=alpha_hat,
                tau_hat_ik=tau_hat_ik))
            ordered_terms.append(term_k)

        probabilities = pref.prob_i(utilities)

        i = np.random.multinomial(1, probabilities).argmax()

        term = ordered_terms[i]

        super().__init__(term=term,
                         start_at=start_at,
                         name='search_google_political',
                         search_type='political',
                         select_result=True,
                         time_spent=30)


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
            utilities.append(pref.media_utility_u_ij(pi_i=pi_i,
                                                     pi_tilde_j=pi_tilde_j,
                                                     epsilon_ij=epsilon_ik,
                                                     alpha_tilde=alpha_tilde,
                                                     tau_tilde_ij=tau_tilde_ij))
            ordered_outlets.append(url)

        probabilities = pref.prob_i(utilities)

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
                         select_result=True,
                         time_spent=5)


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
        domains = pd.read_csv(PRIMEMOVER_PATH + file_path, encoding='utf-16')
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
            jobs.VisitJob(url="https://browserleaks.com/ip", flag='leak_ip',
                          task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))

        # JavaScript
        self.jobs.append(
            jobs.VisitJob(url="https://browserleaks.com/javascript",
                          flag='leak_javascript', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))

        # Webrtc
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/webrtc",
                                       flag='leak_webrtc', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))

        # Canvas
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/canvas",
                                       flag='leak_canvas', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))

        # Webgl
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/webgl",
                                       flag='leak_webgl', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))
        # Fonts
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/fonts",
                                       flag='leak_fonts', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))
        # SSL
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/ssl",
                                       flag='leak_ssl', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))
        # GeoLocation
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/geo",
                                       flag='leak_geo', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))
        # Features
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/features",
                                       flag='leak_features',
                                       task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))
        # Proxy
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/proxy",
                                       flag='leak_proxy', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))

        # Java system
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/java",
                                       flag='leak_java', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))

        # Flash
        self.jobs.append(jobs.VisitJob(url="https://browserleaks.com/flash",
                                       flag='leak_flash', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))

        # Silverlight
        self.jobs.append(
            jobs.VisitJob(url="https://browserleaks.com/silverlight",
                          flag='leak_silverlight', task='BrowserLeaks'))
        self.jobs.append(jobs.Wait(time=r.randint(2, 4)))


class SetGooglePreferences(Queue):
    PASS_CRAWLER = False
    """
    Visit Google and adjust the number of search results
    If Option set_language = 
    """

    def __init__(self, start_at, nr_results=50, set_language=None):
        super().__init__(start_at=start_at,
                         name='Set_Google_Preferences',
                         )

        self.jobs.append(
            jobs.VisitJob(url="https://www.google.com", task=self.name,
                          captcha_mode='never'))
        self.jobs.append(jobs.TryClick(selector_type="XPATH",
                                       selector='//*[@id="Mses6b"]',
                                       task=self.name,
                                       captcha_mode='never'))

        self.jobs.append(jobs.TryClick(selector_type="XPATH",
                                       selector='//*[@id="dEjpnf"]/li[1]',
                                       task=self.name,
                                       captcha_mode='never'))
        self._set_language = set_language
        nr_results = round(nr_results, -1)
        click_dict = {10: (5, 1), 20: (4, 2), 30: (3, 3), 40: (2, 4),
                      50: (1, 5), 100: (0, 6)}

        if nr_results in click_dict.keys():
            position = click_dict[nr_results][1]
            nr_click = click_dict[nr_results][0]
            click_list = 5 * [jobs.TryClick(selector_type="XPATH",
                                            selector=f'//*[@id="result_slider"]/ol/li[{6}]',
                                            task=self.name + '/Nr_Results',
                                            captcha_mode='never')]
            click_list += nr_click * [jobs.TryClick(selector_type="XPATH",
                                                    selector=f'//*[@id="result_slider"]/ol/li[{position}]',
                                                    task=self.name + '/Nr_Results',
                                                    captcha_mode='never')]

            self.jobs = self.jobs + click_list
        else:
            raise ValueError('Can only set 10,20,30,40,50 or 100 results')
        if set_language is not None:
            # switch to language menu
            self.jobs.append(jobs.TryClick(selector_type="XPATH",
                                           selector='//*[@id="langSecLink"]/a',
                                           task=self.name + "/Language",
                                           captcha_mode='never'
                                           ))
            # set the language
            self.jobs.append(jobs.TryClick(selector_type="XPATH",
                                           selector=f'//*[@id="langten"]/div/span[@class="jfk-radiobutton-label"][text()="{self._set_language}"]',
                                           task=self.name + "/Language",
                                           captcha_mode='never'))

        self.jobs.append(jobs.TryClick(selector_type="XPATH",
                                       selector='//*[@id="form-buttons"]/div[1]',
                                       task=self.name,
                                       captcha_mode='never'))
        self.jobs.append(jobs.TryHandleAlertJob("ACCEPT", task=self.name,
                                                captcha_mode='never'))

        self.jobs.append(jobs.Wait(5, task=self.name, captcha_mode='after'))


class HandleCookiesGoogle(Queue):
    PASS_CRAWLER = True

    def __init__(self, crawler, start_at):
        cookie_pref = crawler.configuration.cookie_pref
        super().__init__(start_at=start_at,
                         name='handle_google_cookies',
                         description='handle google cookie pop up according to cookie pref object'
                         )
        self.jobs.append(jobs.VisitJob(url='https://www.google.com',
                                       task=self.name))
        if cookie_pref['accept_all']:
            self.jobs.append(jobs.TryClick(selector_type='CSS',
                                           selector='#L2AGLb > div:nth-child(1)',
                                           captcha_mode='after',
                                           task=self.name))
        else:
            self.jobs.append(jobs.TryClick(selector_type='CSS',
                                           selector='#VnjCcb > div:nth-child(1)',
                                           captcha_mode='after',
                                           task=self.name))
            if cookie_pref.get('SearchCustom', True):
                self.jobs.append(jobs.TryClick(selector_type='CSS',
                                               selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(4) > div.uScs5d > div > div.uScs5d > div:nth-child(2) > div > button > div.VfPpkd-RLmnJb',
                                               captcha_mode='after',
                                               task=self.name))
            else:
                self.jobs.append(jobs.TryClick(selector_type='CSS',
                                               selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(4) > div.uScs5d > div > div.uScs5d > div:nth-child(1) > div > button > div.VfPpkd-RLmnJb',
                                               captcha_mode='after',
                                               task=self.name))
            if cookie_pref.get('YoutubeHist', True):
                self.jobs.append(jobs.TryClick(selector_type='CSS',
                                               selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(5) > div.uScs5d > div > div.uScs5d > div:nth-child(2) > div > button > div.VfPpkd-RLmnJb',
                                               captcha_mode='after',
                                               task=self.name))
            else:
                self.jobs.append(jobs.TryClick(selector_type='CSS',
                                               selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(5) > div.uScs5d > div > div.uScs5d > div:nth-child(1) > div > button > div.VfPpkd-RLmnJb',
                                               captcha_mode='after',
                                               task=self.name))
            if cookie_pref.get('AdCustom', True) == False:
                self.jobs.append(jobs.TryClick(selector_type='CSS',
                                               selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(6) > div.IgeUeb > div.uScs5d > div > div.uScs5d > div:nth-child(1) > div > button > div.VfPpkd-RLmnJb',
                                               captcha_mode='after',
                                               task=self.name))
            elif cookie_pref.get('AdCustom', True) == True:
                self.jobs.append(jobs.TryClick(selector_type='CSS',
                                               selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(6) > div.IgeUeb > div.uScs5d > div > div.uScs5d > div:nth-child(2) > div > button > div.VfPpkd-RLmnJb',
                                               captcha_mode='after',
                                               task=self.name))
            else:

                self.jobs.append(jobs.TryClick(selector_type='CSS',
                                               selector='# yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(6) > div.IgeUeb > div.wIdmhb > div',
                                               captcha_mode='after',
                                               task=self.name))
                cookie_pref['GoogleAds'] = False
                cookie_pref['YoutubeAds'] = False
                if cookie_pref.get('GoogleAds', True):
                    self.jobs.append(jobs.TryClick(selector_type='CSS',
                                                   selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(6) > div.Iwf3xf.sMVRZe > div:nth-child(4) > div > div > div.uScs5d > div:nth-child(2) > div > button > div.VfPpkd-RLmnJb',
                                                   captcha_mode='after',
                                                   task=self.name))
                else:
                    self.jobs.append(jobs.TryClick(selector_type='CSS',
                                                   selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(6) > div.Iwf3xf.sMVRZe > div:nth-child(4) > div > div > div.uScs5d > div:nth-child(1) > div > button > div.VfPpkd-RLmnJb',
                                                   captcha_mode='after',
                                                   task=self.name))
                if cookie_pref.get('YoutubeAds', True):
                    self.jobs.append(jobs.TryClick(selector_type='CSS',
                                                   selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(6) > div.Iwf3xf.sMVRZe > div:nth-child(8) > div > div > div.uScs5d > div:nth-child(2) > div > button > div.VfPpkd-RLmnJb',
                                                   captcha_mode='after',
                                                   task=self.name))
                else:
                    self.jobs.append(jobs.TryClick(selector_type='CSS',
                                                   selector='#yDmH0d > c-wiz > div > div > div > div.VP4fnf > div:nth-child(6) > div.Iwf3xf.sMVRZe > div:nth-child(8) > div > div > div.uScs5d > div:nth-child(1) > div > button > div.VfPpkd-RLmnJb',
                                                   captcha_mode='after',
                                                   task=self.name))
