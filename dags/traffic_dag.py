from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime
import os

PROJECT_ROOT = Variable.get("PROJECT_ROOT")
PYTHON = os.getenv("PYTHON_PATH", "python")

default_args = {
    "start_date": datetime(2025, 1, 1),
    "retries": 1
}

with DAG(
    dag_id="traffic_etl_pipeline",
    default_args=default_args,
    schedule="*/30 * * * *",
    catchup=False
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/scripts/extract.py {PROJECT_ROOT}"
    )

    transform = BashOperator(
        task_id="transform",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/scripts/transform.py {PROJECT_ROOT}"
    )

    load = BashOperator(
        task_id="load",
        bash_command=f"{PYTHON} {PROJECT_ROOT}/scripts/load.py {PROJECT_ROOT}"
    )

    extract >> transform >> load