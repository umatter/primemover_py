# execute "docker build -t "primemover_py" ." in the primemover_py folder
# to run container run

FROM ubuntu:latest


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
RUN . primemover_py/primemover_env/bin/activate && pip3 install -r primemover_py/requirements.txt && pip3 install apache-airflow==1.10.12 \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-1.10.12/constraints-3.7.txt" && airflow initdb && mkdir /root/airflow/dags
COPY primemover_test_dag.py /root/airflow/dags
COPY primemover_dag.py /root/airflow/dags
COPY airflow.cfg /root/airflow/

RUN . primemover_py/primemover_env/bin/activate && airflow initdb
