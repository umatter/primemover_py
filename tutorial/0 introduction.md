# An Introduction to Primemover_py
## a worked example from start to finish

### 0. This Tutorial
This tutorial is intended to guide users of this library through the intricacies
of this package. We begin with a general introduction before creating a few sample
experiments inteded for an investigation of Google search.
The completed code for this specific example is stored in src_google.

### 1. About Primemover
First off, if you haven't done so already, you should clone the repository and run "makefile.sh". To do so,
navigate to the primemover_py directory in your terminal window and 
execute:
```bash
git clone https://github.com/umatter/primemover_py.git
chmod +x makefile.sh
./makefile.sh
```
This library and its dependencies in requirements.txt is known to work with python 3.9.
If you have not previously installed python your best bet for getting this program to work
is to simply follow the steps of the docker file. That is installing python 3.9 before 
creating a virtual environment and running the modules in this file. Do this by executing the 
statements behind the "run" command in your terminal. Note, this will only work for unix
operating systems and is not guaranteed to work with your specific version. If everything does get
installed, py should run fine. If airflow fails to install localy, which is quite likely, this does not prevent
you from running most code locally. If you want to see other requirements check out the requirements.txt file.




The idea behind this program is to control a series of bots via an API. This consists
of ____ key components:
- setting up new bots (crawlers)
- creating and sending new 
- tasks (queues) for crawlers to execute
- updating existing crawlers
- parsing results produced by crawlers.

This means that this library is responsible for three core items, "Crawlers", "Queues" and 
"Results". Since the results are not further processed by the api and runner, the
structure of the other two components is more critical. We therefor begin by discussing the
"Crawler", the "Queue" and their respective components.

### 2. The Crawler
Like all fundamental objects, the BaseCrawler object can be found in src/base. 
The base crawler consists of three core sub-objects:
- Agent: the agent contains information on what the crawlers' browser will look like to websites the crawler visits ("src/base/BaseAgent.py")
- Proxy: the proxy object provides the runner with details on the proxy used for the crawlers browsing ("src/base/BaseProxy.py")
- Config: the config object is perhaps the most vital object from py's perspective,
    as this contains parameters that we in py can use to control bots behavior. The base version
    contains a series of variables some of which may not be useful in future experiments. More can
    always be added, and we will discuss this in an upcoming section. ("src/base/BaseConfig.py")

The crawler itself sits within an "experiment" which is simply a collection of crawlers
that can be controlled together. We use the experiment id assigned by the API to fetch and update crawlers.

### 3. The Queue
A "job" is a very simple instruction for the runner to execute. All available jobs can be found in "src/worker/jobs.py".
Note, jobs are carefully checked for compatability with both the API and most importantly
the runner. Alterations to these jobs should be done with great care and only in coordination with the runner.
This is why they are stored separately from src/base in src/worker. The files contained in worker generalize
to all experiments and should not be overwritten. This is also where we find "PrimemoverQueue.py".
A "queue" is simply a list of jobs to be executed consecutively along with a start time. 
Note, start times are set randomly by default, but we will return to this matter once we consider an example setup.
Consecutive execution means that a single queue assigned to a crawler is equivalent to a single browser session.
Assigning multiple queues to a crawler means that this crawler will run separate browsing sessions. 

Since jobs are very low level instructions such as opening a website, scrolling or clicking, creating a complex browsing session
from jobs would be a hassle. To make the process a little less cumbersome, py has the intermediate object
"Task". A task is simply a collection of jobs that we regularly assign to a bot, such as visiting a website
scrolling around for 30 seconds and clicking on a specific field. Tasks form the basis of our experimental setup
and can be concatenated to form a complex browsing session. "src/base/base_tasks.py" contains some fundamental tasks
that might be useful. We also assign all jobs in a task the field "task": "<name_of_task>". This is critical when 
trying to identify actions in the output returned by the runner. To aid parsing you might also like to
use the "flag" property.

### 4. What's next?
We proceed by creating a small manual example of a new experiment. See the first steps markdown document.
