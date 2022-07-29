# A Complete Experiment
## Updating and Deployment Using Airflow
This section will aim to take the reader from a static setup to one that allows for
automated updates to crawlers and the automation of all processes.
We begin with the setup from the previous section "a more complete setup" and extend it.

### Updating
Updating crawler preferences requires two components. First, we need to alter the Crawler.update_crawler 
and Config.update_config methods. Second we need to parse the reports that are relevant
for any updating behavior and pass this to these functions.

So, as before, we re-define the methods in the "worker/classes" file.
First the update method for the Config object.
The goal of this update is to choose a new set of media oulets and search terms if 
the user was confronted with an unfamiliar outlet or adjusted their political preferences.
The reasoning and exact specification is not relevant here.

We begin by repeating the calls to "history" from the Base config function.
The check `info is not None` is intended to make sure that the config object has already been 
assigned an ID by the API, as this is used to identify the history in the s3 Bucket.

If a history object exists, we pull it and append our changes to it.
```python
 def update_config(self, new_location):
        """
        Update self according to results
        """
        if self.info is not None:
            self.history.pull_existing()
        ...
        # Some change here
        ...
        self.history.update_current_status()
        self.history.push()
```
Part of the default update method is to change the location. This is done here
rather than just setting location to ensure that the history contains this change.
```python
   def update_config(self, new_location):
        ...
        if new_location is not None:
            self.location = new_location
        ...
        self.history.push()
    
```
Now for the core of our new update procedure. Lets pass the update function the two aditional parameters
"results" and "terms". Where results will be a dictionary containing the websites the 
crawler selected while conducting neutral searches and their political orientation.
Don't spend much time here. It is not particularly relevant to setting up a new experiment since this is highly
dependent on the experiment at hand and few aspects will translate!
The idea is simple, adjust the parameters of configurations based on what has been observed. 
To structure the code, some calculations have been moved to the preferences and configuration functions modules.
```python
def update_config(self, results, new_location, terms=True):
    ...
    kappa_j_t = self.kappa
    if results is not None and len(results) > 0:
        pi_0 = self.pi
        for outlet in results:
            if 2 == self.kappa:
                if not outlet['known']:
                    kappa_j_t = 1
                else:
                    kappa_j_t = 0

            self.pi = preferences.political_orientation_pi_i_t(
                psi_i=self.psi, kappa_j_t_prev=kappa_j_t,
                pi_tilde_j_prev=outlet['pi'], pi_i_prev=self.pi)

        self.media = self.CONFIGURATION_FUNCTIONS.update_media_outlets(
            outlets=self.media + results, alpha_tilde=self.alpha,
            pi=self.pi,
            tau_tilde_ij=self.tau, k=10)
        if terms and pi_0 != self.pi:
            self.terms = self.CONFIGURATION_FUNCTIONS.SelectSearchTerms(
                pi=self.pi,
                alpha_hat=self.alpha,
                tau_hat_ik=self.tau,
                k=40)
    ...
    self.history.push()

```
Changing the crawler update method is not too different. As before,
changes to the location are complex and should be done via the update_crawler method.
This is because a change in location affects:
- the proxy
- the agent
- the configuration and its history

This is already part of the BaseCrawler.update_crawler method. 
our extension is to take the results, identify if they belong to the crawler and pass them
to the configuration update method if they are not null.

```python
    def update_crawler(self, results=None, proxy_update=None, terms=True):
        update_location = None
        if proxy_update is not None:
            update_location = self.proxy.update_proxy(proxy_update)
            if update_location == 'not updated':
                update_location = None

        if update_location is not None:
            self.agent.location = update_location
            self.send_agent = True

        results_valid = []
        if results is not None:
            relevant_results = results.get(str(self._crawler_info.crawler_id),
                                           'skip')
            if relevant_results == 'skip':
                return self
            results_selected = [result.get('data') for result in
                                relevant_results]

            results_selected = list(filter(None, results_selected))
            for res in results_selected:
                if res.get('pi') is not None:
                    results_valid.append(res)

        self.configuration.update_config(results_valid, update_location,
                                         terms=terms)
        return self
```
To utilize these update functions once the experiment is running, we extend our script
for sending new queues, by adding
```python
   
    if os.path.exists(
            f'{PRIMEMOVER_PATH}/resources/cleaned_data/{date_time.date().isoformat()}.json'):
        with open(
                f'{PRIMEMOVER_PATH}/resources/cleaned_data/{date_time.date().isoformat()}.json',
                'r') as file:
            cleaned_data = json.load(file)
        for crawler in crawler_list:
            if crawler.flag != 'neutral':
                crawler.update_crawler(results=cleaned_data)  
```
before generating new queues. This code checks if parsed results that we can use
for updating exist and if so, passes these to the update crawler method of each crawler.

### Changes to the setup
For the purposes of this setup I have made a few changes that I don't believe to warrant 
further discussion. In particular, I have added more tasks from the Google Experiment and created 
the selection parser with the corresponding parser dict. Checkout "tutorial/code/more_complete_setup/worker/google_s3_parser.py"
to see the new parser.
I will however briefly discuss changes to the experiment setup.
I have decided to deviate from the original google experiment in this example, in that
I did not include other proxies since these are currently not available for testing.
What is included here is the assignment of privacy settings.
```python
import random as r 
...

    with_privacy = r.sample(crawler_list, k=20)
    for i, crawler in enumerate(with_privacy):
        if i < 3:
            crawler.agent.multilogin_profile.geolocation = 'BLOCK'
        elif i < 6:
            crawler.agent.multilogin_profile.do_not_track = 1
        elif i < 9:
            crawler.agent.multilogin_profile.hardware_canvas = "BLOCK"
        elif i < 12:
            crawler.agent.multilogin_profile.local_storage = False
            crawler.agent.multilogin_profile.service_worker_cache = False
```
(Note, the number of crawlers is now 20 rather than 10)
Doing this after creating the crawlers rather than through configuration functions is
significantly easier. First, there is no requirement to change any other aspect of the crawler
when changing a privacy setting so there is no risk of errors due to a missmatch. Second,
assigning a setting to a random crawler but to exactly 20% is much more challenging to do
in the backend.

### Towards Deployment via Airflow
Let us begin by creating two airflow DAGs that we will need for deployment. The first is
one for initialization, the second for regular updating.
To be able to import the functions we wrote into the airflow DAG, we need to add __init__ files.
Each init file should import the relevant modules in the folder it is in.
E.g. the __init__ file for "tutorial/code" should look something like this:
```python
from . import complete_experiment

__all__ = [complete_experiment]
```

