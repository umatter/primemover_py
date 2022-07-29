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
