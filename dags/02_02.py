import sys
from pathlib import Path

src_path = Path(__file__).resolve().parent.parent / 'src'
sys.path.append(str(src_path))

from main import run_main_02_02_ktb

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

##
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Define the DAG
with DAG(
    '02_02_ktb_pipe_etl_ist_sinir_gelen_yabanci',
    default_args=default_args,
    description='A DAG to run data processing script',
    schedule_interval='0 3 * * *',
    start_date=datetime(2025, 1, 7),
    catchup=False,
) as dag:

    #
    run_data_processing = PythonOperator(
        task_id='run_main_02_02_ktb',
        python_callable=run_main_02_02_ktb,
    )