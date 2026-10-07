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
        bash_command="cd /opt/project/warehouse && python load_data.py",
    )

    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="cd /opt/project/talentpulse_dbt && dbt run",
    )

    run_automation = BashOperator(
        task_id="run_automation_checks",
        bash_command="cd /opt/project/automation && python run_automation.py",
    )

    load_data >> run_dbt_models >> run_automation