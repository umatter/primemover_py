# primemover_py: A python client library for the primemover configuration API

## Aim and content

The [primemover_ui](https://github.com/umatter/primemover_ui/) offers a REST API to programmatically configure the initial bot population and update the bot population dynamically while running experiments. This python library serves as a python client software (wrapper) for this API. It has the following functions:

- wrapper functions around the core API methods to interact with the API from Python. (download/parse the bots' JSON configuration files, change a few values, send the updated configuration files to the API)
- specific bot configuration functions that set/update bot behavioral parameter values. For example, bot utility functions. For example, compute a bot's probabilities of visiting certain websites based on a utility function implemented in this python library and parameter values fetched from the REST API, then add these probabilities as parameter values to the bot's configuration file and send the updated configuration to the API.

Overall, this part of the primemover application contains most the economic details/specifications guiding the bot's decisions/behavior.

## Structure
All relevant code can be found in src. The purpose of this library being the initialization and updating of bot parameters
as well as the assignment of tasks implies that some aspects of this library are intended to be edited by the user.
Code can be found in src, with a few high level programs in the main directory. The main five being
- ConfigurationFunctions.py
- experiment_2.py (Some experiment file, this should be migrated to a dedicated sub folder in a future update)
- Preferences.py
- Results.py
- UpdateExperiment.py.
These files are intended to be somewhat easily edited, although some care should be taken.
It is perhaps best practice to store old files found here in the old experiments folder.
### Preferences
Preferences does not refers to the preferences of bots in the experiment that is to be conducted.
This shapes the current experimental setup. Any bot utility functions
can be found here.

### ConfigurationFunctions
This module determines how parameters are assigned. This includes attributes such as media outlets a bot knows
or its political affiliation. These may be randomly assigned or set to a fixed value. Note, functions 
found in this module are not always called upon initialization. They are only utilized when no parameter
is passed in initialization.  The Preference functions may play a role here and are therefore imported into
this module.

### Results
The functionality in this module shapes how queues processed by the api are parsed and returned.
Note: This module may be mirgrated to worker in a future update. It is more complex than the other
functions but must be updated when altering or extending tasks. (closely related to worker/parser)

### Experiment...
This program, currently experiment_2_Test.py initializes the current experiment.
It should only be run once. Future experiments should make sure to utilize a fresh experiment_id.
Use this program as a guide when creating a new setup.

### UpdateExperiment
Updates to the experiment occur regularly, currently daily. An update can consist
of a variety of changes. Any of the aspects of a bot may be altered. In addition, 
new tasks are set for the next day.

### Worker
The modules in this folder should be handled with care. In particular the classes
defined in Behavior.py, Jobs.py, Queue.py, Agent.py, Proxy.py, ConfigureProfile.py and Profile.py.
These mimic objects defined for the primemover_runner and the primemover_ui. 
Changing these files may lead to errors when pushing to the runner.
Changes to methods, in particular update methods are safe. 

Use Tasks.py to define new taks for a bot to execute. Examples of existing tasks
are google searches for specific terms and website visits.
Tasks can be concatenated and are sent as queues, which represent a single browser session.

#### Data Copy
The module Data copy.py creates copies of key components of the running experiment and creates a backup
in an S3 Bucket. The function create_copy generates the following three e-mails
-   'config_{experiment_id}/single_params.csv'
     (copy of crawler configurations containing only single valued parameters)
-   'config_{experiment_id}/terms.csv'
    (copy of the list of search terms each crawler uses)
-   'config_{experiment_id}/media.csv'
    (copy of the list of media outlets each crawler knows)
-   'selected_{experiment_id}/selections.csv',
    (Table containing the searches run and the sites selected, columns: `````['crawler_id', 'name', 'beta', 'alpha', 'pi', 'tau', 'job_id',
       'finished_at', 'rank', 'skiped', 'url', 'normalizedUrl',
       'd_tilde_i_j_t', 'u_raw', 'u_final', 'exp_u', 'probability', 'epsilon',
       'prob_LowerEnd', 'prob_UpperEnd', 'selected', 'known', 'u_py']`````)

## Docker Image
Steps to launch, navigate to primemover_py using the terminal and run 
```
docker build -t "primemover_py" .  
```
The docker image is created with tag 'latest'
run 
```
docker run -it -p 8080:<PORT>  --name <NAME> primemover_py  
```
this creates the docker container and connects the airflow port to <PORT>.
You are placed in the container. 
Activate the python enviornment
```
cd primemover_py
. primemover_env/bin/activate
```
If your primemover_py package is a raw copy of the github repository, run
```
Makefile.py
```
```
airflow users create \
    --username <USERNAME> \
    --firstname <FIRSTNAME> \
    --lastname <LASTNAME> \
    --role Admin \
    --email <E-MAIL>
 
```
 
Run the following code to launch airflow:
```
airflow webserver
```
Connect a second terminal window and run:
```
airflow scheduler
```
You can run both from the same terminal by running the webserver with the option -D.
This is risky as quitting one of the two processes will not end the other.
If two schedulers are running errors will occur!

The airflow UI is now accessible via your browser under localhost:<PORT>.
If no bots are setup unpause the dag "primemover_test_dag" and execute a dag run without configurations.
Once the run is complete visit "Admin" -> "XComs" and set the return values of the "create_experiment" task
as variables under "Admin" -> "Variables". This ensures that the correct experiment is updated
by the main dag. You can now pause "primemover_test_dag".
Unpause "primemover_dag", make sure this occurs after 10:30, the dag will otherwise execute twice.
There is no need to manually trigger this Dag, it will now proceed to execute every morning.

## Server Setup
Follow docker image setup and the instructions for docker.
