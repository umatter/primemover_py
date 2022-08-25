# First Steps
## The crawler object and pushing a first experiment
We begin by creating a new experiment with a single crawler and assigning it a task.
For the time being we will simply use the base classes found in src/base. Begin by importing
the base crawler and base configurations object.

```python
from src.base.BaseCrawler import BaseCrawler
from src.base.BaseConfig import BaseConfig
```

We do need some input data. First, we need a keys file containing 
username key pairs for proxies and the s3 bucket. (I am working to remove the need
for this file to ensure keys are not stored in plain text). Create a new file "resources/other/keys.json"
and fill it with the following fields.

```json
{"GEOSURF": {"username": "<username>", "password": "<password>"},
"ROTATING": {"username": "<username>", "password": "<password>"},
"PRIVATE": {"username": "<username>", "password": "<password>"},
"PRIMEMOVER":{"username": "<username>", "password": "<password>"},
"S3": {"username": "<username>","Access_Key_ID": "<access_key_id>","Secret_Access_Key":"<secret_access_key>"}}
```

In particular, py checks whether Geosurf proxies and their
locations are valid. To do so, we need to download a list of valid cities from our
s3 bucket. To do so, load the s3_wrapper module and fetch the relevant files.
`python
from src.worker import s3_wrapper
s3_wrapper.update_valid_cities()
`
Don't worry if this files does not exist in the s3 bucket. A version
should be available under "resources/input_data". Py uses the information contained here
to validate that locations will be accepted by the proxy providers and to compute start and end
times in the local timezone of the bot.
For the time being let us simply generate a base crawler and see how we can set and change parameters.

```python
first_crawler = BaseCrawler()
```
The easiest way to see the whole crawler is by using the "as_dict()" method.

```python
first_crawler.as_dict()
```

This should look very similar to the example at "resources/examples/example_base_crawler.json"
At this stage it's worth looking at how we can export and import crawlers and other objects to and from json files.
All core objects that are part of this package, have an as_dict() method as seen above.
This returns a dictionary that is precisely in the format that the API expects. All of these dictionaries can
be stored as json files.
```python
import pathlib
import json
PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

with open(PRIMEMOVER_PATH + "/resources/crawlers/first_crawler.json",
              'w') as file:
        json.dump(first_crawler.as_dict(), file,
                  indent='  ')
```
We can also read this file into a crawler object.
```python
from src.base.BaseCrawler import BaseCrawler
with open(PRIMEMOVER_PATH + "/resources/crawlers/first_crawler.json",
              'w') as file:
        raw_crawler_dict = json.loads(first_crawler.as_dict(), file,
                  indent='  ')
first_crawler = BaseCrawler.from_dict(raw_crawler_dict)
```
All relevant objects have a from_dict method. The Crawler object also has a from_list method 
incase you have multiple crawlers in a list. The crawlers returned by the API, are however in a dictioanry.
These methods are fairly robust to different formats that they might encounter.

We have three options to change parameters. Consider the location. The current default is Auburn Alabama
"US-AL-AUBURN". Let's change it to Phoenix Arizona "US-AZ-PHOENIX". Notice, that it occurs twice.
Once as part of the agent and once in configuration. Changing the parameter retroactively
by running
```python
first_crawler.agent.location = "US-AZ-PHOENIX"
```

and 

```python
first_crawler.configuration.location = "US-AZ-PHOENIX"
``` 

is therefore slightly unsafe.
These risks become more critical as the generation of crawlers becomes more complex. 
It is therefore not advisable to do this. The core of the crawler is really the configuration object.
This is especially true since we can store any number of parameters here that could later influence
choices for the agent. This is reflected by how the crawler is generated. The config object is generated
first using defaults stored at src/base/base_config_functions. The agent is then generated
based of the config function. Therefore, we can generate a crawler in Phoenix Arizona
either by changing the defaults or by generating a config object ourselves and then passing it to the crawler. 
Let's begin by considering the second approach. 

```python
first_config = BaseConfig(location='US-AZ-PHOENIX')
second_crawler = BaseCrawler(configuration = first_config)
print(second_crawler.agent.location)
print(second_crawler.configuration.location)
```
Notice that the agent has the correct location. We will cover changing the defaults in a later chapter.

If we want our crawler to do something we need to assign it tasks. Checkout 
"src/base/base_tasks.py" to see a few examples that you may want to use or build on.
Almost all experiments begin by having crawlers visit browser leaks inorder to ensure that no information
has leaked and that the agent looks as expected. To assign a browser leaks task to our crawler, simpl use the add_task method.

```python
from src.base import base_tasks as tasks
second_crawler.add_task(tasks.BrowserLeaks)
```
To see the Queue you generated, run
```python
second_crawler.queues[0].as_dict()
```
.
Notice, that the queues start_time seems somewhat arbitrary. It has been randomly generated
by the TimeHandler function from a pre-set interval. 
You could set the specific crawlers schedule by assigning it a new one before you generate the Queue.

```python
from src.worker.TimeHandler import TimeHandler
second_crawler.schedule = TimeHandler(second_crawler.agent.location,
                                         interval=120,
                                         wake_time=10 * 60 * 60,
                                         bed_time=17 * 60 * 60
                                         )
```
Note, there is a global schedule parameter, that ensures queues do not clash with each other or runner downtime.

The actual times used will be from the intersection of these ranges. To change the global schedule
run
```python
from src.worker.TimeHandler import Schedule
TimeHandler.GLOBAL_SCHEDULE = Schedule(interval=600,
                                           start_at=14 * 60 * 60,
                                           end_at=(9 + 24) * 60 * 60)
```
Where start and end_at determine the allowed start and 
end times in your local time while interval sets the initial minimum time in seconds between
two queues. Note, this sets the schedule for all crawlers, you generate, not just second_crawler.

This scheduler is perhaps a little cumbersome so we can instead simply set a new time for our Queue
by manually overriding the generated time. 
```python
from datetime import datetime, timedelta
t_0 = datetime.now() + timedelta(minutes=1)
second_crawler.queues[0].start_at = t_0
```
The queue is now set to start in one minute local time.

If we push the crawler now, it is not entirely clear which experiment it belongs to.
Let us instead generate a new experiment and assign the crawler.
```python
from src.worker.Experiment import Experiment
exp = Experiment(
    name='Test Experiment',
    description='A first step towards using primemover_py',
    contact='you',
)
```
This code only generates an empty, local experiment. We need an experiment id to be assigned by the API.
Load the API wrapper and connect to the api by generating keys.
```python
import src.worker.api_wrapper as api
api_credentials = {"username":"<username>","password":"<password>"}

exp_return = api.new_experiment(api_credentials, exp.as_dict())
exp_id = Experiment.from_dict(exp_return).id

print(exp_id)
```
If you already have a test experiment setup you may just want to use that experiment id instead.
Assign the experiment id to the crawler (you can also assign the experiment id when first generating the crawler).
```python
second_crawler.experiment_id = exp_id
```

It is now time to push the new crawler to the API. We first store it as a json file.
```python
import json
import pathlib

#base path to local directory (careful! the parent.parent... list needs to match the levels to return to the root folder. 3 parents, assumes we are 3 folders deep ) 
PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

#Note, the API expects a list of crawlers
with open(PRIMEMOVER_PATH + "/resources/crawlers/experiment_first_steps.json",
              'w') as file:
        json.dump([second_crawler.as_dict()], file,
                  indent='  ')
```
Before using the api_push_new method to upload the data to the api
```python
return_data = api.push_new(api_credentials=api_credentials,
                           path=PRIMEMOVER_PATH + "/resources/crawlers/experiment_first_steps.json")
data_as_dict = json.loads(return_data.text)
with open(
        f'{PRIMEMOVER_PATH}/resources/crawlers/experiment_first_steps_{datetime.now().date().isoformat()}.json',
        'w') as file:
    json.dump(data_as_dict, file, indent='  ')
print(exp_id)
```
Having generated a crawler with a queue, we would now like to have a look at the results.
We use the src/base/Results.py module to do so.
First let us download the results. 

```python
from src.base import Results
Results.fetch_results(api_credentials=api_credentials)
```
The raw results will have been saved under "resources/raw_data/<todays_date>". 
If you wish to run fetch results again on the same day you will have to delete or rename this file.
