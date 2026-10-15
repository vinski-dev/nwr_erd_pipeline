import os
from google.cloud import bigquery


def ingest_bronze_to_bigquery():
    # TODO: Replace with your actual GCP project ID
    project_id = "nwr-data-platform"
    dataset_id = "bronze"

    client = bigquery.Client(project=project_id)

    # Map the generated CSV files to their target BigQuery tables
    file_to_table_map = {
        "bronze_cms_players.csv": "cms_players",
        "bronze_loyalty_members.csv": "loyalty_members",
        "bronze_cms_ratings.csv": "cms_ratings",
        "bronze_promo_redemptions.csv": "promo_redemptions",
    }

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        # Using TRUNCATE for the synthetic data reset.
        # In a real production ELT pipeline, this would be WRITE_APPEND.
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    for filename, table_name in file_to_table_map.items():
        if not os.path.exists(filename):
            print(f"File not found: {filename}. Skipping.")
            continue

        table_ref = f"{project_id}.{dataset_id}.{table_name}"

        print(f"Uploading {filename} to {table_ref}...")
        with open(filename, "rb") as source_file:
            job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
            job.result()  # Wait for the job to complete

        table = client.get_table(table_ref)
        print(f"Successfully loaded {table.num_rows} rows into {table_ref}.")


if __name__ == "__main__":
    ingest_bronze_to_bigquery()
