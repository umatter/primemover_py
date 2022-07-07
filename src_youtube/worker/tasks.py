"""
Task(s) for Youtube

"""

from src.worker import Tasks
from src.worker.PrimemoverQueue import Queue
from src.worker import Jobs
import src.Preferences as Pref
from src.ConfigurationFunctions import NoiseUtility
import random as r
import numpy as np



class YouTubeSearch(Queue):
    """
        Conduct a YouTube search and scroll to the bottom of the page
    """

    def __init__(self,
                 term,
                 start_at,
                 name='YouTubeSearch',
                 description='Open YouTube, enter a search query and select a result.',
                 search_type='',
                 select_result=False
                 ):
        self._search_term = term
        super().__init__(start_at=start_at,
                         name=name,
                         description=description)
        # add job to visit a webpage (YouTube)
        self.jobs.append(Jobs.VisitJob(url='https://www.youtube.com'))

        # add job to click button (agree) (check if needed)
        self.jobs.append(
            Jobs.SingleSelect(
                selector='(//*[@class="VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc IIdkle"])[2]',
                selector_type='XPATH',
                flag=search_type,
                task=name
                )
        )

        # add job to wait one second (next pop-up takes some time to load)
        self.jobs.append(Jobs.Wait(time=1))

        # add job to click button (no thanks) (check if needed)
        self.jobs.append(
            Jobs.SingleSelect(
                selector='//*[@id="dismiss-button"]/yt-button-renderer',
                selector_type='XPATH',
                flag=search_type,
                task=name
            )
        )

        # add job to select the search field via XPATH and job_type the search term
        self.jobs.append(Jobs.EnterText(text=term,
                                        selector='//*[@id="search"]',
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS",
                                        flag=search_type,
                                        task=name),
                         )

        # add job to scroll to bottom
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=5))
        self.jobs.append(Jobs.Scroll(direction='UP',
                                     percentage=100))

        # add job to select a result randomly
        if select_result:
            self.jobs.append(
                Jobs.SingleSelect(selector='//*[@id="contents"]/ytd-video-renderer',
                                  selector_type='XPATH',
                                  decision_type="CALCULATED",
                                  flag=search_type,
                                  task=name
                                  )
            )

            # add job to scroll down 80% of the visited page
            self.jobs.append(Jobs.Scroll(direction='DOWN',
                                         percentage=80))


class VisitYTDirect(Queue):
    """
        Visit a YouTube page and scroll a bit up/down
    """

    def __init__(self, yt_url, start_at):
        self._outlet_url = yt_url
        self._duration = r.randint(2, 5)  # choose scroll time in seconds
        super().__init__(start_at=start_at,
                         name='Visit YouTube Direct',
                         description='Visit a YouTube page and scroll a bit.')
        # Add Job to Visit a media outlet
        self.jobs.append(Jobs.VisitJob(url=self._yt_url, task=self.name))

        # Add Job to scroll down and up for random time
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=self._duration,
                                     task=self.name))
                                     
        self.jobs.append(Jobs.Scroll(direction='UP',
                                     duration=self._duration,
                                     task=self.name))                                            



class VisitChannel(VisitYTDirect):
    PASS_CRAWLER = True
    """
    Directly visit a YouTube channel
    """

    def __init__(self, crawler, start_at):
        media = crawler.configuration.media
        pi_i = crawler.configuration.pi
        alpha_tilde = crawler.configuration.alpha
        tau_tilde_ij = crawler.configuration.tau

        utilities = []
        ordered_channels = []
        for channel in media:
            url = channel['url']
            pi_tilde_j = channel['pi']
            epsilon_ik = NoiseUtility()
            utilities.append(Pref.media_utility_u_ij(pi_i=pi_i,
                                                     pi_tilde_j=pi_tilde_j,
                                                     epsilon_ij=epsilon_ik,
                                                     alpha_tilde=alpha_tilde,
                                                     tau_tilde_ij=tau_tilde_ij))
            ordered_channels.append(url)

        probabilities = Pref.prob_i(utilities)

        i = np.random.multinomial(1, probabilities).argmax()

        url = ordered_channels[i]

        super().__init__(yt_url=url,
                         start_at=start_at)

