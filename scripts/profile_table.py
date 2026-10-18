import os
import pandas as pd
from google.cloud import bigquery


def configure_pandas_display():
    """Ensure pandas doesn't truncate our new health check columns."""
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.colheader_justify", "left")


def run_data_profiler(sql_file_path: str):
    print(f"Executing profiling script: {sql_file_path}...\n")

    client = bigquery.Client()

    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"Could not find {sql_file_path}")

    with open(sql_file_path, "r") as file:
        profiling_script = file.read()

    # Execute the procedural script
    parent_job = client.query(profiling_script)
    parent_job.result()  # Wait for completion

    # Iterate through child jobs to find the final SELECT from the Temp Table
    for child_job in client.list_jobs(parent_job=parent_job):
        if child_job.destination:
            try:
                df = child_job.to_dataframe()
                if not df.empty:
                    return df
            except Exception:
                continue

    return pd.DataFrame()


if __name__ == "__main__":
    configure_pandas_display()

    # 1. Dynamically get the absolute path of the directory this python script is in
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    # 2. Go UP one level to the project root, then into the sql folder
    PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
    sql_path = os.path.join(PROJECT_ROOT, "sql", "bq_data_profiler.sql")

    results_df = run_data_profiler(sql_path)

    if not results_df.empty:
        print("=== 🚀 Automated Data Quality Report ===")
        print(results_df.to_markdown(index=False))
    else:
        print("No results returned. Check the SQL script execution.")
