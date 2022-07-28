"""
Task(s) for Amazon Search.
"""

from src.worker import Tasks
from src.worker.PrimemoverQueue import Queue
from src.worker import Jobs


class AmazonSearch(Queue):
    """
        Conduct an Amazon search and scroll to the bottom of the page
    """

    def __init__(self,
                 term,
                 start_at,
                 name='AmazonSearch',
                 description='Open Amazon, enter a search query and select a result.',
                 search_type='',
                 select_result=False
                 ):
        self._search_term = term
        super().__init__(start_at=start_at,
                         name=name,
                         description=description)
        # add job to visit a webpage (Amazon)
        self.jobs.append(Jobs.VisitJob(url='https://www.amazon.com'))

        # add job to select the search field via XPATH and job_type the search term
        self.jobs.append(Jobs.EnterText(text=term,
                                        selector='//input[@job_type="text"]',
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

        # add job to select a result randomly; select based on channel, click on search result
        if select_result:
            self.jobs.append(
                Jobs.SingleSelect(click_selector="//div/span[@data-component-job_type='s-product-image']/a/@href | //li/div/a[2]/@href | //div[@class='rhf-footer']//li/span/a/@href",
                                  click_selector_type='XPATH',
                                  criteria_extractor="(?<=\/dp\/)(.*?)(?=\/)",
                                  criteria_selector_type='XPATH',
                                  decision_type="CALCULATED",
                                  flag=search_type,
                                  task=name
                                  )
            )

            # add job to scroll down 80% of the visited page
            self.jobs.append(Jobs.Scroll(direction='DOWN',
                                         percentage=80))
