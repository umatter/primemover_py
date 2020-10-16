FROM UBUNTU

RUN sudo apt update
RUN sudo apt -y upgrade
RUN sudo apt install -y git
RUN sudo apt install -y python
RUN sudo apt install -y python3-pip

RUN git pull()
