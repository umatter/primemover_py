"""Use this file to define your own Tasks, as queue objects.
 Use help(jobs) to see available job types.
 J.L. 07/2022
 """
from src.worker.PrimemoverQueue import Queue
from src.worker import jobs
from tutorial.code.more_complete_setup.worker import preferences as pref
from tutorial.code.more_complete_setup.worker.config_functions import NoiseUtility

from src.base.base_tasks import VisitDirect

import numpy as np
import random as r

import pathlib

PRIMEMOVER_PATH = str(
    pathlib.Path(__file__).parent.parent.parent.parent.parent.absolute())


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
                                     flag=search_type))  # Add Job to select a result randomly
        if select_result:
            self.jobs.append(
                jobs.SingleSelect(selector='.//div[@class="yuRUbf"]/a',
                                  selector_type='XPATH',
                                  decision_type="CALCULATED",
                                  flag=search_type,
                                  task=name,
                                  captcha_mode='always'
                                  )
            )

            # Add Job to scroll down 80% of the visited page
            self.jobs.append(jobs.Scroll(direction='DOWN',
                                         duration=self._time_spent,
                                         captcha_mode='always',
                                         task=name))


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



class VisitMediaNoUtility(VisitDirect):
    PASS_CRAWLER = True
    """
    Conduct a google political search and scroll to the bottom of the page
    """

    def __init__(self, crawler, start_at):
        media = crawler.configuration.media
        url = r.choice(media).get('url')
        super().__init__(outlet_url=url,
                         start_at=start_at)


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
