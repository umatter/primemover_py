from datetime import timedelta, datetime
import sys

PATH_MODULES = "/primemover_py"
sys.path += [PATH_MODULES]

# The DAG object; we"ll need this to instantiate a DAG
from airflow.models import Variable

from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
import src



default_args = {
    "owner": "johannesl",
    "depends_on_past": False,
    "start_date": datetime(2021, 1, 1),
    "email": ["johannesl@me.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=15),
    "catchup": False,
    # "queue": "bash_queue",
    # "pool": "backfill",
    # "priority_weight": 10,
    # "end_date": datetime(2020, 1, 1),
    # "wait_for_downstream": False,
    # "dag": dag,
    # "sla": timedelta(hours=2),
    # "execution_timeout": timedelta(seconds=300),
    # "on_failure_callback": some_function,
    # "on_success_callback": some_other_function,
    # "on_retry_callback": another_function,
    # "sla_miss_callback": yet_another_function,
    # "trigger_rule": "all_success"
}
dag = DAG(
    dag_id="BrowserLeaks",
    default_args=default_args,
    description="Add Browser Leaks tasks",
    schedule_interval=None,
    catchup=False
)

# t1, t2 and t3 are examples of tasks created by instantiating operators

t1 = PythonOperator(
    task_id="setup_copy",
    python_callable=src.base.DataCopy.setup_copy,
    op_kwargs={"experiment_id": Variable.get("experiment_id", "id_missing"),
               "date": datetime.now().date(),
               "api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)
               },
    dag=dag
)

t2 = PythonOperator(
    task_id="addTasks",
    python_callable=src.base.browser_leaks.single_update,
    op_kwargs={"date_time": datetime.now(),
               "experiment_id": Variable.get("experiment_id", "id_missing"),
               "api_credentials": Variable.get("PRIMEMOVER",
                                               deserialize_json=True)
               },
    dag=dag
)

t3 = PythonOperator(
    task_id="cleanup",
    python_callable=src.worker.CleanUp.cleanup,
    op_kwargs={"date_time": datetime.now(),
               "nr_days": 5},
    dag=dag)


t1 >> t2 >> t3
