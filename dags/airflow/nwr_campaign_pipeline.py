from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

# Dynamically resolve absolute paths relative to this DAG file
DAG_DIR = os.path.dirname(os.path.abspath(__file__))
# Going up two levels from dags/airflow/ to reach the root /d/dev/nwr_erd_analytics/
PROJECT_ROOT = os.path.abspath(os.path.join(DAG_DIR, "..", ".."))

INGEST_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "scripts", "erd_data_generator.py")
DBT_PROJECT_DIR = os.path.join(PROJECT_ROOT, "nwr_erd_pipeline")
EXTRACT_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "scripts", "extract_campaign_data.py")
# Add the path to your new profiler script
PROFILER_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "scripts", "profile_table.py")

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "nwr_end_to_end_campaign_pipeline",
    default_args=default_args,
    description="Full ELT: Ingestion -> dbt Build -> Dashboard Extraction & Profiling",
    schedule="0 5 * * *",
    start_date=datetime(2026, 10, 17),
    catchup=False,
    tags=["nwr", "elt", "dbt", "executive_dashboard", "data_quality"],
) as dag:

    ingest_raw_data = BashOperator(
        task_id="ingest_raw_data",
        bash_command=f'python "{INGEST_SCRIPT_PATH}"',
    )

    dbt_build = BashOperator(
        task_id="dbt_build_models",
        bash_command=f'cd "{DBT_PROJECT_DIR}" && dbt build --full-refresh',
    )

    extract_dashboard_data = BashOperator(
        task_id="extract_dashboard_data",
        bash_command=f'python "{EXTRACT_SCRIPT_PATH}"',
    )

    # The new Observability task
    run_pipeline_health_profiler = BashOperator(
        task_id="run_pipeline_health_profiler",
        bash_command=f'python "{PROFILER_SCRIPT_PATH}"',
    )

    # Pipeline Orchestration Dependencies
    # Bronze -> Silver/Gold -> [Extract, Profile]
    ingest_raw_data >> dbt_build >> [extract_dashboard_data, run_pipeline_health_profiler]
