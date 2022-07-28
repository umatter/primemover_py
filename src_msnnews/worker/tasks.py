"""
Task(s) for Bing News Search.

"""

from src.worker import Tasks
from src.worker.PrimemoverQueue import Queue
from src.worker import Jobs


class BingNewsSearch(Queue):
    """
        Conduct a Bing News search and scroll to the bottom of the page
    """

    def __init__(self,
                 term,
                 start_at,
                 name='BingNewsSearch',
                 description='Open Bing News Search, enter a search query and select a result.',
                 search_type='',
                 select_result=False
                 ):
        self._search_term = term
        super().__init__(start_at=start_at,
                         name=name,
                         description=description)

        # add job to visit Bing News Search
        self.jobs.append(Jobs.VisitJob(url='https://www.bing.com/news/'))

        # add job to click button (agree) (check if needed)
        # self.jobs.append(
        #    jobs.SingleSelect(
        #        selector="//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc']",
        #        selector_type='XPATH',
        #        flag=search_type,
        #         task=name
        #     )
        # )

        # add job to select the search field via XPATH and job_type the search term
        self.jobs.append(Jobs.EnterText(text=term,
                                        selector='//*[@id="sb_form_q"]',
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS",
                                        flag=search_type,
                                        task=name),
                         )

        # add job to wait one second (articles take some time to load)
        self.jobs.append(Jobs.Wait(time=1))

        # add job to scroll to bottom
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=5))

        # add job to scroll up
        self.jobs.append(Jobs.Scroll(direction='UP',
                                     percentage=100))

        # add job to select a result randomly
        if select_result:
            self.jobs.append(
                Jobs.SingleSelect(selector='//a[@class="title"]',
                                  selector_type='XPATH',
                                  decision_type="CALCULATED",
                                  flag=search_type,
                                  task=name
                                  )
            )

            # add job to scroll down 80% of the visited page
            self.jobs.append(Jobs.Scroll(direction='DOWN',
                                         percentage=80))
