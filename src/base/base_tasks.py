"""Use this file to define your own Tasks, as queue objects.
 Use help(jobs) to see available job types.
 TODO re-structure tasks into a folder system for different tasks. Perhaps a base folder for reoccouring tasks and separate folders for different experiments.
 J.L. 03/2021
 """
from src.worker.PrimemoverQueue import Queue
from src.worker import Jobs
import random as r
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

class VisitDirect(Queue):
    """
        Visit a website and scroll for 2-3 minutes
    """

    def __init__(self, outlet_url, start_at):
        self._outlet_url = outlet_url
        self._duration = r.randint(30, 60)  # choose scroll time in seconds
        super().__init__(start_at=start_at,
                         name='Visit Direct',
                         description='Visit a media outlet and scroll for 2-3 minutes.')
        # Add Job to Visit a media outlet
        self.jobs.append(Jobs.VisitJob(url=self._outlet_url, task=self.name))

        # Add Job to scroll down for random time between 1 and 3 minutes
        self.jobs.append(Jobs.Scroll(direction='DOWN',
                                     duration=self._duration,
                                     task=self.name))

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
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))

        # JavaScript
        self.jobs.append(
            Jobs.VisitJob(url="https://browserleaks.com/javascript",
                          flag='leak_javascript', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))

        # Webrtc
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/webrtc",
                                       flag='leak_webrtc', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))

        # Canvas
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/canvas",
                                       flag='leak_canvas', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))

        # Webgl
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/webgl",
                                       flag='leak_webgl', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))
        # Fonts
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/fonts",
                                       flag='leak_fonts', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))
        # SSL
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/ssl",
                                       flag='leak_ssl', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))
        # GeoLocation
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/geo",
                                       flag='leak_geo', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))
        # Features
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/features",
                                       flag='leak_features',
                                       task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))
        # Proxy
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/proxy",
                                       flag='leak_proxy', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))

        # Java system
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/java",
                                       flag='leak_java', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))

        # Flash
        self.jobs.append(Jobs.VisitJob(url="https://browserleaks.com/flash",
                                       flag='leak_flash', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))

        # Silverlight
        self.jobs.append(
            Jobs.VisitJob(url="https://browserleaks.com/silverlight",
                          flag='leak_silverlight', task='BrowserLeaks'))
        self.jobs.append(Jobs.Wait(time=r.randint(2, 4)))
