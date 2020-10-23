
from datetime import timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization

from src.worker import gdelt_gkg
from src import GenerateBenignTerms

default_args = {
    'owner': 'johannesl',
    'depends_on_past': False,
    'start_date': days_ago(0),
    'email': ['johannesl@me.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2020, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
dag = DAG(
    'test_1',
    default_args=default_args,
    description='A first test schedule',
    schedule_interval=timedelta(days=1),
)

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = PythonOperator(
    task_id='neutral_terms',
    python_callable=gdelt_gkg.main,
    op_kwargs={'nr_results': 30},

    dag=dag,
)

t2 = PythonOperator(
    task_id='benign_terms',
    python_callablee=GenerateBenignTerms.GenerateBenignTerms,
    dag=dag,
)

t3 = BashOperator(
    task_id='update',
    bash_command='python3 python3 src/UpdateExperiment.py',
    dag=dag,
)

t4 = BashOperator(
    task_id='say',
    bash_command='print "evereything worked!"',
    dag=dag,
)

t1 >> t2 >> t4
