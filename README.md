# primemover_py: A python client library for the primemover configuration API

## Aim and content

The [primemover_ui](https://github.com/umatter/primemover_ui/) offers a REST API to programmatically configure the initial bot population and update the bot population dynamically while running experiments. This python library serves as a python client software (wrapper) for this API. It has the following functions:

- wrapper functions around the core API methods to interact with the API from Python. (download/parse the bots' JSON configuration files, change a few values, send the updated configuration files to the API)
- specific bot configuration functions that set/update bot behavioral parameter values. For example, bot utility functions. For example, compute a bot's probabilities of visiting certain websites based on a utility function implemented in this python library and parameter values fetched from the REST API, then add these probabilities as parameter values to the bot's configuration file and send the updated configuration to the API.

Overall, this part of the primemover application contains most the economic details/specifications guiding the bot's decisions/behavior.


## Docker Image
If your primemover_py package is a raw copy of the github repository, run
```
Python Makefile.py
```
You may also wish to copy any relevant input data into the corresponding folders.
In particular any data necessary for updating must be present.

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

Run the following code to launch airflow:
```
airflow scheduler &
airflow webserver
```
The airflow ui is now accessible at localhost:<PORT>
