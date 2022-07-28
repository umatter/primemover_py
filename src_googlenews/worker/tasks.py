"""
Task(s) for GoogleNews Search.

"""

from src.base import base_tasks
from src.worker.PrimemoverQueue import Queue
from src.worker import jobs


class GoogleNewsSearch(Queue):
    """
        Conduct a GoogleNews search and scroll to the bottom of the page
    """

    def __init__(self,
                 term,
                 start_at,
                 name='GoogleNewsSearch',
                 description='Open GoogleNews, enter a search query and select a result.',
                 search_type='',
                 select_result=False
                 ):
        self._search_term = term
        super().__init__(start_at=start_at,
                         name=name,
                         description=description)

        # add job to visit a webpage (YouTube)
        self.jobs.append(jobs.VisitJob(url='https://www.news.google.com'))

        # add job to click button (agree) (check if needed)
        self.jobs.append(
            jobs.SingleSelect(
                selector="//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc']",
                selector_type='XPATH',
                flag=search_type,
                task=name
            )
        )

        # add job to select the search field via XPATH and job_type the search term
        self.jobs.append(jobs.EnterText(text=term,
                                        selector='//input[@class="Ax4B8 ZAGvjd"]',
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS",
                                        flag=search_type,
                                        task=name),
                         )

        # add job to wait one second (articles take some time to load)
        self.jobs.append(jobs.Wait(time=1))

        # add job to scroll to bottom
        self.jobs.append(jobs.Scroll(direction='DOWN',
                                     duration=5))

        # add job to scroll up
        self.jobs.append(jobs.Scroll(direction='UP',
                                     percentage=100))

        # add job to select a result randomly
        if select_result:
            self.jobs.append(
                jobs.SingleSelect(selector='/html/body/c-wiz[2]/div/div[2]/div[2]/div/main/c-wiz/div[1]/div',
                                  selector_type='XPATH',
                                  decision_type="CALCULATED",
                                  flag=search_type,
                                  task=name
                                  )
            )

            # add job to scroll down 80% of the visited page
            self.jobs.append(jobs.Scroll(direction='DOWN',
                                         percentage=80))
