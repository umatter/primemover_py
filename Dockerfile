# execute "docker build -t "primemover_py" ." in the primemover_py folder
# to run container run

FROM ubuntu:20.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install tzdata
RUN apt-get upgrade -y


ENV TZ=CET
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN dpkg-reconfigure --frontend noninteractive tzdata

RUN apt update
RUN apt -y upgrade


RUN apt install -y python3.9 python3-pip
RUN apt install -y python3.8-venv

COPY /src /primemover_py/src
COPY /resources /primemover_py/resources
COPY requirements.txt /primemover_py/
COPY /src_amazon /primemover_py/src_amazon
COPY /src_google /primemover_py/src_google
COPY /src_googlenews /primemover_py/src_googlenews
COPY /src_msnnews /primemover_py/src_msnnews
COPY /src_yahoonews /primemover_py/src_yahoonews
COPY /src_youtube /primemover_py/src_youtube
COPY /tutorial /primemover_py/tutorial

RUN pip3 install --upgrade setuptools


RUN cd primemover_py && python3 -m venv primemover_env
RUN . primemover_py/primemover_env/bin/activate && pip3 install -r primemover_py/requirements.txt && pip3 install apache-airflow==2.1.0 \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.1.0/constraints-3.8.txt" && airflow db init&& mkdir /root/airflow/dags

#COPY airflow.cfg /root/airflow/

RUN . primemover_py/primemover_env/bin/activate && airflow db init
