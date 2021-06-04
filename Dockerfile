# execute "docker build -t "primemover_py" ." in the primemover_py folder
# to run container run

FROM ubuntu:latest

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install tzdata

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN dpkg-reconfigure --frontend noninteractive tzdata

RUN apt update
RUN apt -y upgrade


RUN apt install -y python3.8 python3-pip
RUN apt-get install python3.8-venv

COPY /src /primemover_py/src
COPY /resources /primemover_py/resources
COPY requirements.txt /primemover_py/
COPY Makefile.py /primemover_py/
COPY Main.py /primemover_py/

RUN pip3 install --upgrade setuptools


RUN cd primemover_py && python3.8 -m venv primemover_env
RUN . primemover_py/primemover_env/bin/activate && pip3 install -r primemover_py/requirements.txt && pip3 install apache-airflow==2.1.0 \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.1.0/constraints-3.8.txt" && airflow db init&& mkdir /root/airflow/dags
COPY primemover_test_dag.py /root/airflow/dags
COPY primemover_dag.py /root/airflow/dags
COPY new_experiment_dag.py /root/airflow/dags
COPY airflow.cfg /root/airflow/

RUN . primemover_py/primemover_env/bin/activate && airflow db init
