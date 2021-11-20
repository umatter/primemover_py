from datetime import timedelta, datetime
import sys

PATH_MODULES = '/primemover_py'
sys.path += [PATH_MODULES]

# The DAG object; we'll need this to instantiate a DAG
from airflow.models import Variable

from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
import src

default_args = {
    'owner': 'johannesl',
    'depends_on_past': False,
    'start_date': datetime(2021, 1, 1),
    'email': ['johannesl@me.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=15),
    'catchup': False,
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
    'update_emergency_2',
    default_args=default_args,
    description='update crawler config and tasks and upload csvs',
    schedule_interval=None,
    catchup=False
)

# t1, t2 and t3 are examples of tasks created by instantiating operators


# t2 = PythonOperator(
#     task_id='parse_all_results',
#     python_callable=src.Results.process_results,
#     op_kwargs={'set_reviewed': True,
#                'parser_dict': src.worker.s3_parser.ParserDict,
#                'path_end': 'all_data_',
#                'date_time': datetime.now()},
#     dag=dag)
#
# t3 = PythonOperator(
#     task_id='upload_results',
#     python_callable=src.worker.s3_wrapper.upload_data,
#     op_kwargs={'filename': f'output/{datetime.now().date_time().isoformat()}.json',
#                'path': f'/resources/cleaned_data/all_data_{datetime.now().date_time().isoformat()}.json'},
#     dag=dag)
#
# t4 = PythonOperator(
#     task_id='parse_search_results',
#     python_callable=src.Results.process_results,
#     op_kwargs={'set_reviewed': False,
#                'parser_dict': src.worker.s3_parser.UpdateParser,
#                'date_time': datetime.now()},
#     dag=dag)
#
#
#

t5 = PythonOperator(
    task_id = 'csv_hist',
    python_callable = src.worker.DataCopy.create_copy,
    op_kwargs={'experiment_id': Variable.get("experiment_id", 'id_missing')},
    dag =dag
)

t6 = PythonOperator(
    task_id='update_crawlers',
    python_callable=src.UpdateExperiment.single_update,
    op_kwargs={'date_time': datetime.now(),
               'experiment_id': Variable.get("experiment_id", 'id_missing'),
               'fixed_times': Variable.get("fixed_times", False),
               'delta_t_1': Variable.get("delta_t_1", 120),
               'delta_t_2': Variable.get("delta_t_2", 36)},
    dag=dag
)

t7 = PythonOperator(
    task_id='cleanup',
    python_callable=src.worker.CleanUp.cleanup,
    op_kwargs={'date_time': datetime.now(),
               'nr_days': 5},
    dag=dag)

t5 >> t6 >> t7
