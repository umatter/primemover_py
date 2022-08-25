# A more complete setup
## From a single crawler to a full setup
Building on the previous example, we will now consider a more complete setup. The goal here will be to create a few crawlers
that search google and a program to push new queues and parse their results. This is fundamentally the first step to creating src_google/experiment_2.py.
The code created here can be found under "tutorial/code/more_complete_setup".
### New Defaults
Let us first change the defaults for the configuration functions and privacy settings.
We create a copy of src/base/base_config_functions.py at tutorial/code/more_complete_setup/worker/config_functions.py and change the functions to 
suit the defaults we would like. For the Google experiment this means re-defining how search
terms are assigned (SelectSearchTerms), from the base which simply assigns an 
empty list. We also alter SelectMediaOutlets for the same reason. If you have a look at the analogous
at the file in src_google, you will see these changes. There are others,
but we will return to these later. 

### New Classes
While the setup in first steps was able of simply using the classes from src/base this will not work in this setting.
The Google experiment requires elements that are not relevant to other experiments, and we will begin by accommodating these differences.

To re-define the base classes, we create subclasses for BaseCrawler, BaseAgent, BaseProxy and BaseProfile. Initially, we change nothing, except
the classes of the objects each class expects as arguments and we make sure that the classes use 
our new configuration functions.

```python
"""Re-Define base classes to make changes that render them usable for the Google Experiment"""

from src.base.BaseAgent import BaseAgent
from src.base.BaseProfile import BaseProfile
from src.base.BaseProxy import BaseProxy
from src.base.BaseConfig import BaseConfig
from src.base.BaseCrawler import BaseCrawler

from datetime import datetime

#Import the new configuration functions
from src_google.worker import config_functions


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
    # Note, we haven't changed anything in these configuration functions, but I add this for completeness
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
    # Change set of configuration functions to Google Specific setup
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
                 cookie_pref=None,
                 info=None,
                 date_time=datetime.now()
                 ):
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
```
This code will only change the defaults at the moment, along with the names of the classes.
The Google experiment setup requires a few more changes since we need to change the setter
for terms and media and add the additional parameter usage type.

We first amend the getters and setters for media and terms. We add the following code to the Config class:
```python

    @BaseConfig.media.setter
    def media(self, media_in):
        if media_in is None:
            # Initialize from configuration functions
            self._media = self.CONFIGURATION_FUNCTIONS.SelectMediaOutlets(
                pi=self._pi,
                alpha_tilde=self.alpha,
                tau_tilde_ij=self.tau,
                k=1,
                local=1)
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
            # Initialize from configuration functions
            self._terms = self.CONFIGURATION_FUNCTIONS.SelectSearchTerms(
                pi=self.pi,
                alpha_hat=self.alpha,
                tau_hat_ik=self.tau,
                k=2)

        elif type(term_dict) is list:
            # valid type, so simply use it
            self._terms = term_dict
        elif type(term_dict) is dict:
            # valid type, so simply use it
            self._terms = term_dict
        elif type(term_dict) is str and term_dict != "":
            # This seems to be a json, we try to convert it to a dict or list
            self._terms = json.loads(term_dict)
        elif term_dict == "":
            self._terms = ""
        else:
            raise TypeError(
                f'terms should be a dict job_type object containing search terms')
```
The class can now use the new configuration functions correctly.
Next we add the new parameter  "usage_type". This requires a few steps. First we 
have to add usage_type to the __init__ method.
```python
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
                 ###### HERE #####
                 usage_type=None,
                 #################
                 cookie_pref=None,
                 info=None,
                 date_time=datetime.now()
                 ):
        #### HERE ######
        self.usage_type = usage_type
        ################
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
```
Adding the parameter also means that we should define a getter and setter. This 
is not strictly speaking a requirement but is good practice.
```python
# Getter
@property
def usage_type(self):
    return self._usage_type

# Setter
@usage_type.setter
def usage_type(self, val):
    # Decide what to do with the value that is passed.
    if (val is None) or (val == "Value not provided at update!"):
        val = self.CONFIGURATION_FUNCTIONS.usage_type()
    elif type(val) is str:
        val = val.lower().strip()
    if val in ['only_search', 'only_direct', 'both']:
        self._usage_type = val
    else:
        raise ValueError('Not a valid value for usage_type')
```
Note, the setter we define here references the configuration functions. So we should make sure
to add a "usage_type" function there.

```python
import random as r
def usage_type():
    choice = \
        r.choices(['only_search', 'only_direct', 'both'], [0.25, 0.25, 0.5])[0]
    return choice
```
If you were to generate a crawler from this new class, it would have the usage_type property. 
The method as_dict(), we used in the first steps tutorial doesn't know this however.
We need to add it to the as dict method as a preference object. 

```python
def as_dict(self, send_info=False):
    # Generate the usual dict
    base_dict = super().as_dict(send_info)
    # Add the usage_type
    usage_type_preference = {
        "name": 'usage_type',
        "value": self.usage_type
    }

    base_dict["preferences"].append(usage_type_preference)

    return base_dict
```
Unless a new parameter is implemented in the API directly, it must be added in this manner.

To cap it off, we can re-define the default schedule. This is part of the crawler class.
All we need to do is change the setter for the schedule.
```python
from src.worker.TimeHandler import TimeHandler
class Crawler(BaseCrawler):
    ...
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
```
Notice that the new schedule uses the location we assigned to the agent (the agent location is by default the configuration location).
So if we now set different locations for different bots, the timezones will be considered in scheduling.

### New Tasks
Having amended the crawlers to suit our expanded requirements, we can now create tasks for crawlers to execute.
For this small setup, we will have to create a few new tasks. To create new tasks, we create the file 
"tutorial/code/more_complete_setup/worker/tasks.py" and begin by importing the PrimemoverQueue object since it forms
the basis for all tasks.
```python
from src.worker.PrimemoverQueue import Queue
```
We can now build a queue that consists of conducting one Google search.
Begin by defining the class GoogleSearch as a subclass of Queue. Because we will generalize
the class later by defining different types of GoogleSearches, let us create the 
parameter search_type. We might also want to choose whether or not to select a result
so we also include a parameter for this choice.
```python

class GoogleSearch(Queue):
    """
    Conduct a google search and scroll to the bottom of the page
    """

    def __init__(self,
                 term,
                 start_at,
                 name='GoogleSearch',
                 description='Open Google, enter a search query and optionally select a result.',
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
```
This will initialize a queue object and give us a few extra parameters to work with.
A queue fundamentally consists of a list of jobs which is initially empty. We can
simply append new jobs to this list. We first need to go to google.
```python
        # Add Job to Visit a webpage (google)
        self.jobs.append(
            jobs.VisitJob(url='https://www.google.com', captcha_mode='always',
                          task=name))
```
The runner will navigate to Google. We now select the search field and submit our query
```python
# Add Job to select the search field via XPATH and job_type the search term
        self.jobs.append(jobs.EnterText(text=term,
                                        selector="//input[@name='q']",
                                        selector_type='XPATH',
                                        send_return=True,
                                        type_mode="SIMULATED_FIXINGTYPOS",
                                        task=name,
                                        captcha_mode='always'),

                         )
```
Notice, the EnterText job requires some text to be typed and some form of HTML selector.
To avoid loading issues, we briefly scroll to the bottom of the page and back up.
```python
        # Add Job to scroll to bottom
        self.jobs.append(jobs.Scroll(direction='DOWN',
                                     percentage=100,
                                     captcha_mode='always', task=name))
        self.jobs.append(jobs.Scroll(direction='UP',
                                     percentage=100,
                                     captcha_mode='always',
                                     task=name,
                                     flag=self._search_type))  # Add Job to select a result randomly
```
It is critical to use the flag parameter at some point in order to identify the job for parsing later! Having multiple jobs with
the same flag will lead to both being parsed. This is not true for the single select job, as this job changes the assigned flag
to "<decision_type>/<flag>". 

Finally, if desired, we select a result and scroll through the page we are now on.
The job SingleSelect_New will replace the old SingleSelect job in the upcoming version
of the runner. It allows the use of the criteria extractor field to guide a decision process
implemented in the runner.

```python
        if select_result:
            self.jobs.append(
                jobs.SingleSelect_New(
                    click_selector='.//div[@class="yuRUbf"]/a',
                    click_selector_type='XPATH',
                    decision_type="CALCULATED",
                    criteria_extractor='^(?:https?\:\/\/)?(?:www.)?([^\/?#]+)(?:[\/?#]|$)',
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
```

This GoogleSearch task uses now additional information from the crawler or some other file.
we can however pass the crawler to a queue in order to use its properties. Say we want a crawler
to conduct a political google search, where the crawler selects a search term that is
closely aligned with its political ideology. In that case we can use the parameters pi and the stored list of terms
to decide what to search. To tell the crawler to pass itself, simply set the Class constant
PASS_CRAWLER to True. Since this political search is still a Google Search and nothing really
changes, we can re-use this class.

```python
from tutorial.code.more_complete_setup.worker.config_functions import NoiseUtility
import tutorial.code.more_complete_setup.worker.preferences as pref
import numpy as np

class PoliticalSearch(GoogleSearch):
    #Set this variable True to ensure the crawler is passed
    PASS_CRAWLER = True
    """
    Conduct a google political search and scroll to the bottom of the page
    """
    # Pass crawler, to access pi and terms
    def __init__(self, crawler, start_at, term_type=None):
        # Fetch terms from configuration and select what to search for.
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
        # conduct a search using the selected term.
        super().__init__(term=term,
                         start_at=start_at,
                         name='search_google_political',
                         search_type='political',
                         select_result=True,
                         time_spent=30)

```
Critically, we changed the name and search_type! These parameters will later show
up in the behaviours flag and task when the results are returned. This means we can distinguish
the political searches from others making it possible to parse only select jobs.

We need a few more tasks, including one to handle Google's cookie questions, but we won't discuss
these here. You can find all of them in the "more_complete_setup/worker/tasks.py" file.

### Set up
The setup for this new experiment is virtually identical to the one we saw in the first part of this introduction.
To house the experiment setup we create a new folder in "/more_complete_setup/" called "experiment" and create a copy of first steps.py.

Since we changed aspects of our base classes and renamed them, we first need to switch all these references. Critically, 
our new defaults require a csv containing outlets and one containing terms. If available,
we should fetch these from the s3 bucket along with the list of valid cities.

```python
# Classes are now imported from our worker/classes file
from tutorial.code.more_complete_setup.worker.classes import Crawler, Config, Proxy

# We will start with a browser leaks queue, so lets load the base tasks
from src.base import base_tasks as tasks

from src.worker import s3_wrapper
from src.worker.TimeHandler import TimeHandler, Schedule
from src.worker import api_wrapper as api
from datetime import datetime, timedelta
from src.worker.Experiment import Experiment

import json
import pathlib

PRIMEMOVER_PATH = str(
    pathlib.Path(__file__).parent.parent.parent.parent.parent.absolute())

def first_experiment(api_credentials, update_files=False, push=True):
    """
    Param:
        update_files, Bool: If False, first_crawler will not attempt to fetch valid_cities, outlets and terms from s3
        push, Bool: if False, no new experiment will be created and no queues will be pushed
    """
    api_token = api.get_access(api_credentials.get('username'),
                               api_credentials.get('password'))
    if update_files:
        s3_wrapper.update_valid_cities()
        s3_wrapper.fetch_outlets()
        s3_wrapper.fetch_terms()
        
    exp = Experiment(
        name='Test Experiment',
        description='A first step towards using primemover_py',
        contact='you',
    )
    if push:
        exp_return = api.new_experiment(api_token, exp.as_dict())
        exp_id = Experiment.from_dict(exp_return).id
    else:
        exp_id = 0    
    
    first_config = Config(location='US-AZ-PHOENIX')

    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)


    second_crawler = Crawler(configuration=first_config, experiment_id=exp_id)

    second_crawler.add_task(tasks.BrowserLeaks)
    ...
    return exp_id
```

This crawler will already be different from the one we generated in first steps, since
it uses different defaults and has the usage_type parameter.
A single user does not make an experiment so let us generate 10 instead. In previous
experiments we often generated bots in pairs of 5, 1 neutral (pi=0) 2 left (pi<0) and 2 right (pi>0)
where the ones on the left had the exact opposite pi of those on the right. This time 
let us place the bots in Oakland California "US-CA-OAKLAND" and New York "US-CA-OAKLAND".

```python
GEO_SURF_PROXIES = ["US-CA-OAKLAND",
                        "US-CA-OAKLAND"]
# generate neutral configurations
# Giving a configuration a name <Name>/<text> assigns the configuration the flag <text>. This can then be used for configuring or assigning
# different tasks
    config_list_neutral = [
        Config(name='Config/neutral', location=l, pi=0) for
        l in 1 * GEO_SURF_PROXIES]
    # generate crawlers from neutral configs
    # the flag for the crawler is automatically taken from config, the assignment here is therefore redundant.
    crawler_list = [
        Crawler(flag='neutral', configuration=c, experiment_id=exp_id) for
        c in
        config_list_neutral]
    # generate left and right configs with opposing pi in each location
    config_list_left = [Config(name='Config', location=l, flag='left')
                        for l in
                        2 * GEO_SURF_PROXIES]
    config_list_right = [
        Config(name='Config',
               location=left_config.location,
               pi=-left_config.pi) for left_config in
        config_list_left]
    
    # Make Crawlers from the left and right config lists
    crawler_list += [
        Crawler(configuration=c, experiment_id=exp_id) for c
        in
        config_list_right + config_list_left]

```
Having created local versions of the crawlers, we once again assign each crawler 
a browser leaks queue and reset the time to a fixed interval between queues.

```python
[crawler.add_task(tasks.BrowserLeaks) for crawler in crawler_list]
t_0 = datetime.now() + timedelta(minutes=5)
for crawler in crawler_list:
    crawler.queues[0].start_at = t_0
    t_0 += timedelta(minutes = 2)
```
The load procedure is identical to that in the first steps case.

```python
    with open(
            PRIMEMOVER_PATH + "/resources/crawlers/more_complete_setup.json",
            'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')
    
    return_data = api.push_new(access_token=api_token,
                               path=PRIMEMOVER_PATH + "/resources/crawlers/more_complete_setup_.json")
    data_as_dict = json.loads(return_data.text)
    with open(
            f'{PRIMEMOVER_PATH}/resources/crawlers/more_complete_setup_{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')

```

### New Queues
Having created our crawlers, we can start sending them new Queues.
This consists of three parts:
1. Fetching the Crawlers
2. Adding Queues locally
3. Uploading to the API

We therefore begin by downloading the crawlers. This is where the experiment ID comes in handy.
```python
from tutorial.code.more_complete_setup.worker.classes import Crawler
from tutorial.code.more_complete_setup.worker import tasks
from src.worker.TimeHandler import Schedule, TimeHandler
from datetime import datetime, timedelta
import src.worker.api_wrapper as api_wrapper
import json
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


def single_update(date_time, experiment_id,api_crdentials):
    
    api_token = api_wrapper.get_access(api_credentials.get('username'),
                               api_credentials.get('password'))
    
    #Again we set the global schedule
    TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)
    # Fetch the experiment we created earlier
    raw_experiment = api_wrapper.fetch_experiment(access_token=api_token, id=
    experiment_id)
    
    # Create python objects from the json returned by the API
    crawler_list = Crawler.from_list(raw_experiment['crawlers'],
                                             date_time=date_time)
```
This gets us back to the exact same point that we were at when we added
the browser leaks queues to the crawlers during the initial setup. As such, we can 
simply add Queues at this point!

```python
import tutorial.code.more_complete_setup.worker.tasks as tasks 
for crawler in crawler_list:
    # create a queue and begin by accepting Googles cookie preferences
    session_id = crawler.add_task(tasks.HandleCookiesGoogle, to_session=True)

    if crawler.flag in {'left', 'right'} and \
            crawler.configuration.usage_type != 'only_direct':
        crawler.add_task(tasks.PoliticalSearch,
                            to_session=session_id)
    if crawler.flag in {'left', 'right'} and \
            crawler.configuration.usage_type != 'only_search':
        crawler.add_task(tasks.VisitMediaNoUtility,
                            to_session=session_id)

    crawler.add_task(tasks.GoogleSearch, to_session=session_id,
                        params={'term': 'Joe Biden'})
```
As we did before, we can reset the start times of the queues we just generated. But let us increase
time between queues to three minutes to give the runner more time to handle the tasks we assigned.
```python
t_0 = datetime.now() + timedelta(minutes=5)
for crawler in crawler_list:
    crawler.queues[0].start_at = t_0
    t_0 += timedelta(minutes = 2, seconds=30)
```
The only thing left to do is sending the queues to the API. The process is identical to before. (Note, the option 
"object_ids" determines if the IDs assigned by the API should be sent with objects below the crawler level.)
```python
with open(PRIMEMOVER_PATH + "/resources/updates/generated.json",
          'w') as file:
    json.dump(
        [crawler.as_dict(object_ids=False) for crawler in crawler_list],
        file,
        indent='  ')
        return_data = api_wrapper.push_new(access_token=api_token,
                               path=f'{PRIMEMOVER_PATH}/resources/updates/generated.json')
    # can only store return data if status code == 200
    if return_data.status_code == 200:
        with open(
                f'{PRIMEMOVER_PATH}/resources/updates/{date_time.date().isoformat()}.json',
                'w') as file:
            json.dump(return_data.json(), file, indent='  ')
```

At this point we have created a new set of crawlers, and have the ability to assign them new queues. As in first steps we would
also like to take a look at the results returned by the runner. As before, we begin by fetching the completed queues from the API.
```python
from src.base import Results
Results.fetch_results(api_token=api_token)
```
This is not particularly useful, even if we filter out the crawlers that we are interested in,
we need to identify the specific jobs we are interested in and parse the information from the
reports stored in the s3 Bucket. Results.py is intended to handle this, but we will first need to extend the 
methods that it uses to parse the results. Checkout src/base/s3_parser.py to see what is already available.
To create parsers for different jobs, we begin by importing the base_s3_parser module.
```python
from src.base.base_s3_parser import *
```
Let us build two different new Parsers of Google search results. The first will simply take a results page and return
the rank, title, body and url of each search result along with the search term that led to this result.
Any parser function will be passed three arguments.
1. All behaviors of the job being parsed
2. report data, which can be just the html or the dynamic report (what data to pass here, will be determined by the parser dict)
3. job_id

Even if the specific parser does not require three fields, they must exist to prevent an error.
The base assumption of our parser will be that we are passed data from a task that has navigated 
us to where we expect to be. We begin by establishing some baseline information. In particular,
we confirm that the html from the report is not empty
and check that there is no reference to captchas 

```python
def GoogleParser(behaviors, raw_html, job_id):
    if raw_html is None:
        return {'issue': 'unknown'}

    if 'captcha' in str(raw_html):
        print(f'Captcha: {job_id} ')
        return {'issue': 'Captcha'}
```
Next we extract the aforementioned information we are interested in using beautiful soup.
Note, there is a small tool in src.worker.utility to extract the domain from a URL.
```python
from bs4 import BeautifulSoup
from src.worker.utilities import extract_domain
def GoogleParser(behaviors, raw_html, job_id):
    ...
    soup = BeautifulSoup(raw_html, "html.parser")
    results_in = soup.find_all(class_='g')
    if len(results_in) == 0:
        results_in = soup.find_all(class_='rc')
    
    parsed_data = []
    for rank, result in enumerate(results_in):
        try:
            url = result.find('a').get('href')
        except:
            url = ''
            print('URL is missing')
        try:
            domain = extract_domain(url)
        except:
            domain = ''
    
        try:
            title = result.find('h3').text
        except:
            title = ''
            # Title is missing
        try:
            body = result.find(class_='IsZvec').text
        except:
            # Body is missing
            body = ''
```
Finally, all data gathered should be summarized in a single dictionary.
```python
    ...
    parsed_data.append(
            {'rank': rank, 'title': title, 'url': url,
             'body': body,
             'domain': domain})

    return parsed_data
```
To tell the functions of the Results module to use this new parser, we add it to a parser dict. We have already imported the 
base pareser dict which checks for browser leaks tasks and captchas. Let us add our new parser to this dict.
The parser dict works by assigning a parser to a job if the flag matches. The google search tasks we built earlier assign
flags twice. Once: <search_type> and once <selection_type>/<seach_type>. For the time being we want to use our
parser for the scroll job which assigns <search_type>. This will therefore be the key for our dictionary entries.
we pass two parameters:
- method: the parser we just defined
- data: the portion of the report the parser requires as its second argument. For our parser
    this is 'html'
```python
ParserDict['google_search'] = {'method': GoogleParser, 'data': 'html'}
ParserDict['political'] = {'method': GoogleParser,
                           'data': 'html'}
```
After fetching our results as before, we can now run:
```python
from src.base import Results
#import the parser dict we just updated
from tutorial.code.more_complete_setup.worker.google_s3_parser import ParserDict
Results.process_results(api_credentials=KEYS.get("PRIMEMOVER"),set_reviewed=False,parser_dict=ParserDict, path_end='parsed_')
```
