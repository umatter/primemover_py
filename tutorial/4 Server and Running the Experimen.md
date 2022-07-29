# Server and Running the Experiment
Launch a terminal and navigate to the ssh keys for your server. Then run
```bash
ssh -i primemover.key -L 8080:localhost:8080 ubuntu@86.119.43.115
```
to connect to the server.
If docker is not yet installed, run 
```bash
sudo apt install docker.io
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

