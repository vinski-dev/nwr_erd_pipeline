import os
import glob
from google.cloud import storage
from google.cloud import bigquery

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ID = "nwr-data-platform"
BUCKET_NAME = "nwr-landing-zone-bronze"
DATASET_ID = "casino_platform"  # Ensure this dataset exists in BigQuery
SOURCE_DIR = "./optimized_erd_data"
GCS_PREFIX = "raw_ingest/"


# ==========================================
# 1. UPLOAD TO GOOGLE CLOUD STORAGE
# ==========================================
def upload_to_gcs(local_file_path, bucket_name, gcs_blob_name):
    """Uploads a local file to a GCS bucket."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob_name)

    print(f"Uploading {local_file_path} to gs://{bucket_name}/{gcs_blob_name}...")
    blob.upload_from_filename(local_file_path)
    return f"gs://{bucket_name}/{gcs_blob_name}"


# ==========================================
# 2. LOAD INTO BIGQUERY FROM GCS
# ==========================================
def load_gcs_to_bigquery(gcs_uri, dataset_id, table_name):
    """Loads a CSV file from GCS into a BigQuery native table."""
    bq_client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{dataset_id}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip CSV header
        autodetect=True,  # Let BQ infer schema (INT, FLOAT, STRING, TIMESTAMP)
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite for this demo
    )

    print(f"Loading {gcs_uri} into BigQuery table {table_id}...")
    load_job = bq_client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)

    load_job.result()  # Wait for the job to complete

    # Fetch table metadata to confirm
    destination_table = bq_client.get_table(table_id)
    print(f"Successfully loaded {destination_table.num_rows} rows to {table_id}.\n")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Ensure source directory exists
    if not os.path.exists(SOURCE_DIR):
        raise FileNotFoundError(f"Source directory '{SOURCE_DIR}' not found. Run the generator script first.")

    csv_files = glob.glob(os.path.join(SOURCE_DIR, "*.csv"))

    if not csv_files:
        print("No CSV files found to ingest.")

    for file_path in csv_files:
        # Extract table name from filename (e.g., 'bronze_cms_ratings.csv' -> 'bronze_cms_ratings')
        file_name = os.path.basename(file_path)
        table_name = os.path.splitext(file_name)[0]

        gcs_blob_name = f"{GCS_PREFIX}{file_name}"

        # Step 1: Local to GCS
        gcs_uri = upload_to_gcs(file_path, BUCKET_NAME, gcs_blob_name)

        # Step 2: GCS to BigQuery
        load_gcs_to_bigquery(gcs_uri, DATASET_ID, table_name)

    print("All datasets successfully ingested to GCP!")
