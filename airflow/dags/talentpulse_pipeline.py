from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "talentpulse",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="talentpulse_daily_pipeline",
    default_args=default_args,
    description="TalentPulse: load data, run dbt models, run automation checks",
    schedule_interval="@daily",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["talentpulse"],
) as dag:

    load_data = BashOperator(
        task_id="load_data_to_warehouse",
        bash_command="echo 'Loading data into warehouse (see warehouse/load_data.py in repo)'",
    )

    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="echo 'Running dbt models to refresh KPIs (see talentpulse_dbt/ in repo)'",
    )

    run_automation = BashOperator(
        task_id="run_automation_checks",
        bash_command="echo 'Running automation rules and sending alerts (see automation/run_automation.py in repo)'",
    )

    load_data >> run_dbt_models >> run_automation
    