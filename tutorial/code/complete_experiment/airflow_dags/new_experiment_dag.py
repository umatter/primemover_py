from datetime import timedelta, datetime
import sys

PATH_MODULES = "/primemover_py"
sys.path += [PATH_MODULES]
# The DAG object; we"ll need this to instantiate a DAG

from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable

from tutorial.code import complete_experiment

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization



default_args = {
    "owner": "<Owner Here>",
    "depends_on_past": False,
    "start_date": datetime(2021, 1, 1),
    "email": ["johannesl@me.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=15),
    "catchup": False
}
dag = DAG(
    "new_experiment",
    default_args=default_args,
    description="create new crawlers",
    schedule_interval=None,
    catchup=False
)


t1 = PythonOperator(
    task_id="create_experiment",
    python_callable=complete_experiment.experiment.experiment_setup.launch_experiment,
    dag=dag,
    op_kwargs={"api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)}
)

t1
