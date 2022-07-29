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

Let us also add some new tasks. In particular, let us add a "neutral" search. The search terms
come from the s3 bucket and are to be searched one after the other, one each day.
This is to occour in a separate Queue.

First, we load the neutral terms
```python
 "Fetch Neutral terms from s3 Bucket"
    neutral_path = PRIMEMOVER_PATH + '/resources/input_data/neutral_searchterms_pool.json'
    if not os.path.exists(neutral_path):
        neutral_in = s3_wrapper.fetch_neutral()
    else:
        with open(neutral_path) as file:
            neutral_in = json.load(file)
    nr_neutral = 1
    neutral = []
    if len(neutral_in) < nr_neutral:
        neutral_in += s3_wrapper.fetch_neutral()
        with open(neutral_path, 'w') as file:
            json.dump(neutral_in, file)
    for i in range(nr_neutral):
        neutral.append(neutral_in.pop(0))
```
To add a separate Queue from the one we have already assigned, we simply don't pass the 
session_id. If we also want these Queues to be scheduled separately, we can replace the
crawlers' scheduler.
```python
    for c in crawler_list:
        c.schedule = TimeHandler("US-CA-LOS_ANGELES",
                                 interval=120,
                                 wake_time=18 * 60 * 60,
                                 bed_time=21 * 60 * 60,
                                 date_time=date_time)
        session_id = c.add_task(tasks.HandleCookiesGoogle,
                                to_session=True)
        c.add_task(tasks.NeutralGoogleSearch, to_session=session_id,
                   params={'term': neutral[1]})
```

Finally, we will handle the reset of start times differently this time. First of all,
the previous setups only had one queue per crawler, and we were able to simply select queues[0].
Secondly, the previous setup had crawlers search in the same order every time. 
The TimeHandler has already randomized the order, and we can use this fact.
```python
        queues_1 = [c.queues[0] for c in crawler_list]
        queues_1.sort(key=lambda q: datetime.fromisoformat(q.start_at))
        t_0 = datetime.fromisoformat(queues_1[0].start_at)
        delta_t_1 = int(delta_t_1)
        for q in queues_1:
            q.start_at = t_0.isoformat()
            t_0 += timedelta(seconds=delta_t_1)

        queues_2 = [c.queues[1] for c in crawler_list]
        queues_2.sort(key=lambda q: datetime.fromisoformat(q.start_at))
        t_0 = datetime.fromisoformat(
            f'{date_time.date().isoformat()}T21:00:00-06:00')
        delta_t_2 = int(delta_t_2)
        for q in queues_2:
            q.start_at = t_0.isoformat()
            t_0 += timedelta(seconds=delta_t_2)

```
where we will set delta_t_1 and delta_t_2 externally.


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
Having added these __init__ files to all folders we are interested in, we can now
setup our first airflow dag (directed acyclic graph). For the purposes of the experiments
we have run in the past, these were quite straightforward.

Let us first create a DAG which runs the experiment setup script.
To do so we need to specify a path and load modules from it.
```python
from datetime import timedelta, datetime
import sys

PATH_MODULES = "/primemover_py"
sys.path += [PATH_MODULES]
# The DAG object; we"ll need this to instantiate a DAG

from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable

from tutorial.code import complete_experiment
import src
```

Next we can set default parameters for our DAG and initialize it.
```python
default_args = {
    "owner": "<Owner Here>",
    "depends_on_past": False,
    "start_date": datetime(2021, 1, 1),
    "email": ["johannesl@me.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=15),
    "catchup": False
}

dag = DAG(
    "new_experiment",
    default_args=default_args,
    description="create new crawlers",
    schedule_interval=None,
    catchup=False
)

```
If one wants the dag to run immediately, the start_date option has to be in the past.
This particular DAG has schedule_interval = None since we want it to run when triggered only and do not intend
to repeat it.
Finally we assign tasks to this DAG. In our case this is a call of the launch_experiment function
in experiment_setup.py. 
```python
t1 = PythonOperator(
    task_id="create_experiment",
    python_callable=complete_experiment.experiment.experiment_setup.launch_experiment,
    dag=dag,
    op_kwargs={"api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)}
)

t1
```
Use op_kwargs to pass named parameters. Here I pass "api_credentials". These credentials are stored as airflow variables.
We will see how to set these variables later on when we install and launch airflow.

I create two more DAGs, one pushes browser leaks jobs for these crawlers using the src/base/browser_leaks.py
module and I wont discuss it here.

The second DAG will be the core of the application. The initial setup of the DAG is identical. With two key
exceptions. 

```python
dag = DAG(
    dag_id="update",
    default_args=default_args,
    description="update crawler config and tasks",
    schedule_interval="30 8 * * *",
    catchup=False
)
```
Here, the  value of schedule_interval is "30 8 * * *" which is a CRON schedule.
This specific one will start the DAG at 8:30 every day. Note, the time will be in UTC
not your local time.

The first step of our update procedure will be to fetch results and parse them.
```python
t1 = PythonOperator(
    task_id="fetch_results",
    python_callable=src.base.Results.fetch_results,
    op_kwargs={"date": datetime.now().date(),
               "api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)},
    dag=dag,
)

t2 = PythonOperator(
    task_id="parse_all_results",
    python_callable=src.base.Results.process_results,
    op_kwargs={"set_reviewed": True,
               "parser_dict": complete_experiment.worker.google_s3_parser.ParserDict,
               "path_end": "all_data_",
               "date": datetime.now().date(),
               "process": "ALL",
               "api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)
               },
    dag=dag)

```
Before we upload the parsed results to the s3 Bucket.

```python
t3 = PythonOperator(
    task_id="upload_results",
    python_callable=src.worker.s3_wrapper.upload_data,
    op_kwargs={"filename": f"output/{datetime.now().date().isoformat()}.json",
               "path": f"/resources/cleaned_data/all_data_{datetime.now().date().isoformat()}.json"},
    dag=dag)

```
To generate the results file for updating, We parse the results again, this time with the UpdateParser
```python

t4 = PythonOperator(
    task_id="parse_search_results",
    python_callable=src.base.Results.process_results,
    op_kwargs={"set_reviewed": False,
               "parser_dict": complete_experiment.worker.google_s3_parser.UpdateParser,
               "date_time": datetime.now(),
               "process": "neutral search",
               "api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)
               },
    dag=dag)
```
This particular experiment includes the automated selection of search results. Since
this is implemented in the runner, primemover_py includes a copy of the selection functionality
and can be run to validate the selection. This is done using google_data_copy.py. The base version of the module
src/base/DataCopy.py 's  setup copy function simply copies all parameters of the configuration object into s3. 
If this is a desired feature, in a new experiment, you can orientate yourself using this 
function, else simply use the base DataCopy function.
```python
t5 = PythonOperator(
    task_id="csv_hist",
    python_callable=complete_experiment.worker.google_data_copy.create_copy,
    op_kwargs={"experiment_id": Variable.get("experiment_id", "id_missing"),
               "date": datetime.now().date(),
               "api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)
               },
    retries=2,
    dag=dag
)
```
This task fails occasionally due to connection issues. Hence the retries are set to 2.

Nextup is the core of the update:
```python

t6 = PythonOperator(
    task_id="update_crawlers",
    python_callable=complete_experiment.experiment.update_experiment.single_update,
    op_kwargs={"date_time": datetime.now(),
               "experiment_id": Variable.get("experiment_id", "id_missing"),
               "delta_t_1": int(Variable.get("delta_t_1", 120)),
               "delta_t_2": int(Variable.get("delta_t_2", 36)),
               "api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)
               },
    dag=dag
)
```
It is essential to set the experiment ID as a variable once we have created the experiment!

Tasks seven and eight are more administrative. Task seven sends an E-Mail on success.
While task 8 delete old files to prevent the server from running out of disc space.
```python

t7 = PythonOperator(
    task_id="send_mail",
    python_callable=src.base.Notify.send_update,
    op_kwargs={"email_list": Variable.get("email_list",
                                          deserialize_json=True),
               "password": Variable.get("email_password", "password_missing"),
               "date": datetime.now().date()},
    dag=dag)

t8 = PythonOperator(
    task_id="cleanup",
    python_callable=src.worker.CleanUp.cleanup,
    op_kwargs={"date_time": datetime.now(),
               "nr_days": 5},
    dag=dag)
```
As a final line, we will need to add the order in which tasks are to be executed.
```python
t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7 >> t8
```
It might also be worthwile to create smaller versions of the DAG running from 5 to 8 for example. This is helpful when
some portion of the DAG fails, as we won't have to re-run all of it and will avoid mistakes in the final
output.
