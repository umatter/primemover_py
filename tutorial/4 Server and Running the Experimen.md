# Server and Running the Experiment
Launch a terminal and navigate to the ssh keys for your server. Then run
```bash
ssh -i primemover.key -L 8080:localhost:8080 ubuntu@86.119.43.115
```
to connect to the server.
If docker is not yet installed, run 
```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get -y install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
    
sudo mkdir -p /etc/apt/keyrings    
curl -fsSL -y https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
    ```
Git should be pre-installed. Since this repository is public, simply run
```bash
git clone https://github.com/umatter/primemover_py.git
```
The repository should now be available!
Let's begin by running the makefile.
```bash
cd primemover_py
sh makefile.sh
```
While still in the primemover folder run 
```bash
docker build -t "primemover_py" .  
```
You might be missing permissions. In that case, run
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker 
```
before retrying the previous command.

This will run for a long time if there is no prior version of the docker image.

The docker image is created with the tag 'latest'
run 
```bash
docker run -it -p 8080:<PORT>  --name <NAME> primemover_py  
```
to launch the container.
This creates the docker container and connects the airflow port to <PORT>.
You are placed in the container. 
Activate the python enviornment
```bash
cd primemover_py
. primemover_env/bin/activate
```

Next we need to create an airflow user. Do this by running
```bash
airflow users create \
    --username <USERNAME> \
    --firstname <FIRSTNAME> \
    --lastname <LASTNAME> \
    --role Admin \
    --email <E-MAIL>
```
You will be prompted to choose a password.

Finally, to launch airflow, run 
```
airflow webserver &
airflow scheduler 
```
This runs the two separate processes that make up the airflow.

You can now connect to the airflow GUI by visiting "localhost:<PORT>" in your browser. 

There should not be any DAGs visible right now. To add the DAGs we created earlier
enter ctrl+c and 
"exit". This exits the docker image completely and stops airflow from running! Never do this
in the live version. Only do this when you intend to change the code, this requires airflow to be 
restarted. 
By running 
```bash
docker ps -a
```
you can see the container Experiment and its status to confirm.

To copy a file into the docker container we use the command
```bash
docker cp <src-path> <container>:<dest-path> 
```
hence we need to run 
```bash
docker cp -a primemover_py/tutorial/code/complete_experiment/airflow_dags Experiment:/root/airflow/dags 
```
While we are at it, let us also add the keys file to our container. We first need to copy it to the server.
In a second terminal window run:
```bash
Copy resources % scp -i <PATH/primemover.key> <PATH_PRIMEMOVER_PY/resources/other/keys.json> ubuntu@86.119.43.115:~/primemover_py/resources/other/keys.json
```
Where the first path is for the ssh key, while the second goes to the file we intend to copy.
Back in the first terminal window we can now run 
```bash
docker cp primemover_py/resources/other/keys.json Experiment:/primemover_py/resources/other/keys.json
```
We will also need to update the config file for airflow. It contains the credentials for the e-mail address
and we can't download these from Github. You should generate a key via your e-mail provider and
enter it in the smtp section of src/airflow.cfg.
Then Copy it to the server as we did above and run
```bash
docker cp primemover_py/src/ariflow.cfg Experiment:/root/airflow/
```


To re-launch the container run
```bash
 docker container restart Experiment
```
and 
```bash
docker exec -it Experiment /bin/bash
```
to launch an interactive shell.
We can now restart airflow just as we did before.

```bash
cd primemover_py
. primemover_env/bin/activate

airflow webserver &
airflow scheduler 
```
The dags we created should now be visible.
Navigate to the airflow GUI in your browser.
To trigger a single instance of a DAG, simply click the play button. The DAG will run immediately.
This is appropriate for DAGs that are intended to be triggered manually such as the 
new_experiment_dag. Other DAGs such as the update_dag, that are repeated at specific intervals, are started 
by toggling the pause/unpause switch on the left. The DAG will be run immediately!! So, if the DAG will trigger
at 7, and you unpause it at 6, it will be triggered twice!!

Before we can run our DAGs, we need to fill in the missing airflow variables.
Navigate to Admin, Variables and add a new record. Assign the key 
PRIMEMOVER and as a value a JSON type object
```json
{"username": "<username>",
  "password": "<password>"}
```
akin to the keys.json file.
You can now trigger the new_experiment DAG by clicking play.
Before running the update dag, we will need to add a few more variables to airflow.
- key: experiment_id, value: int, Note, the new experiment dag will return this. You can find the value under Xcoms 
- key: fixed_times, value: True/False
- key: update_preferences, value: True/False (determines whether crawlers are updated or not)
- key: update_proxies value: True/False,
- key: delta_t_1, value: int, time in seconds between first set of Queues
- key: delta_t_2, value: int, time in seconds between second set of Queues
- key: email_list, value: list of e-mail addresses (e.g. ["max.mustermann@e-mail.com, "maximiliane.musterfrau@e-mail.com"]
- key: email_password, value: e-mail password

Do not put these values in quotes!

Once you have entered these values you are good to go and can start the update procedure by unpairing it.
