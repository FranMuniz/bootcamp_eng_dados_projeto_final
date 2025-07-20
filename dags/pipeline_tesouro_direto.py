from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "fran",
    "start_date": datetime(2025, 7, 19),
}

with DAG(
    "pipeline_tesouro_direto",
    default_args=default_args,
    schedule_interval='*/10 * * * *',  # executa a cada 10 minutos
    catchup=False,
    max_active_runs=1  # para evitar execuções simultâneas
) as dag:

    bronze = BashOperator(
        task_id="run_bronze",
        bash_command="python /opt/airflow/dags/scripts/bronze.py"
    )

    silver = BashOperator(
        task_id="run_silver",
        bash_command="python /opt/airflow/dags/scripts/silver.py"
    )

    gold = BashOperator(
        task_id="run_gold",
        bash_command="python /opt/airflow/dags/scripts/gold.py"
    )

    bronze >> silver >> gold
