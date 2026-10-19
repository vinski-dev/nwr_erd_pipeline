from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
import sys

DAG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(DAG_DIR, "..", ".."))

INGEST_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "scripts", "erd_data_generator.py")
DBT_PROJECT_DIR = os.path.join(PROJECT_ROOT, "nwr_erd_pipeline")
EXTRACT_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "scripts", "extract_campaign_data.py")
PROFILER_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "scripts", "profile_table.py")

PYTHON_CMD = sys.executable

# 1. Dynamically grab the credentials (works for both Docker's env vars or WSL's local file)
GCP_KEY_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.path.join(
    PROJECT_ROOT, "credentials", "nwr-data-platform-c2074f9bcf41.json"
)


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

    # 2. Force the export directly in the bash shell before running the script
    ingest_raw_data = BashOperator(
        task_id="ingest_raw_data",
        bash_command=f'export GOOGLE_APPLICATION_CREDENTIALS="{GCP_KEY_PATH}" && "{PYTHON_CMD}" "{INGEST_SCRIPT_PATH}"',
    )

    profile_raw_data = BashOperator(
        task_id="profile_raw_data",
        bash_command=f'export GOOGLE_APPLICATION_CREDENTIALS="{GCP_KEY_PATH}" && "{PYTHON_CMD}" "{PROFILER_SCRIPT_PATH}"',
    )

    dbt_build = BashOperator(
        task_id="dbt_build_models",
        bash_command=f'export GOOGLE_APPLICATION_CREDENTIALS="{GCP_KEY_PATH}" && cd "{DBT_PROJECT_DIR}" && dbt build --full-refresh',
    )

    extract_dashboard_data = BashOperator(
        task_id="extract_dashboard_data",
        bash_command=f'export GOOGLE_APPLICATION_CREDENTIALS="{GCP_KEY_PATH}" && "{PYTHON_CMD}" "{EXTRACT_SCRIPT_PATH}"',
    )

    profile_transformed_data = BashOperator(
        task_id="profile_transformed_data",
        bash_command=f'export GOOGLE_APPLICATION_CREDENTIALS="{GCP_KEY_PATH}" && "{PYTHON_CMD}" "{PROFILER_SCRIPT_PATH}"',
    )

    (ingest_raw_data >> profile_raw_data >> dbt_build >> [extract_dashboard_data, profile_transformed_data])
