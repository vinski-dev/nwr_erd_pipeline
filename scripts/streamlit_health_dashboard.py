import os
import pandas as pd
import streamlit as st
from google.cloud import bigquery

# 1. Page Configuration
st.set_page_config(page_title="Data Quality Gates", page_icon="🛡️", layout="wide")

# Dynamically point to the project credentials (same as the DAG)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        PROJECT_ROOT, "credentials", "nwr-data-platform-c2074f9bcf41.json"
    )


# 2. Data Fetching with Caching (Prevents re-running the BQ scan on every click)
@st.cache_data(ttl=3600)
def fetch_profiling_data(sql_file_path: str):
    client = bigquery.Client()

    if not os.path.exists(sql_file_path):
        st.error(f"SQL file not found at: {sql_file_path}")
        return pd.DataFrame()

    with open(sql_file_path, "r") as file:
        script = file.read()

    try:
        # Execute the query directly and convert to DataFrame
        query_job = client.query(script)
        df = query_job.to_dataframe()
        return df
    except Exception as e:
        st.error(f"BigQuery execution error: {e}")
        return pd.DataFrame()


# Apply best-practice classification tagging for Raw vs Transformed layers
def classify_pipeline_stage(table_name):
    # Standard dbt prefixes (fct_, dim_, stg_, int_) indicate transformed layers
    if any(str(table_name).lower().startswith(prefix) for prefix in ["fct_", "dim_", "stg_", "int_"]):
        return "Transformed / dbt Models"
    return "Raw / Post-Ingestion"


# 4. Dashboard UI Elements
st.title("🛡️ Data Observability & Health Profiler")
st.markdown("Automated schema validation, uniqueness checks, and completeness tracking.")

# --- Sidebar Filters ---
st.sidebar.header("Filter Pipeline Data")

# Stage Filter Slicer
selected_stage = st.sidebar.radio("Pipeline Stage", ["Raw / Post-Ingestion", "Transformed / dbt Models"])

# Determine the absolute directory where your current Streamlit script lives
# current_dir = os.path.dirname(os.path.abspath(__file__))

# Dynamically select the correct SQL file based on the sidebar choice
if selected_stage == "Raw / Post-Ingestion":
    sql_path = "sql/bq_data_profiler_01.sql"
else:
    sql_path = "sql/bq_data_profiler_transformed.sql"

# Debug print to verify the file is found and readable
# st.write(f"Loading SQL from: {sql_path} (Exists: {os.path.exists(sql_path)})")

# Load Data dynamically based on the selected stage
with st.spinner(f"Executing {selected_stage} Profiling Gates in BigQuery..."):
    df = fetch_profiling_data(sql_path)

if df.empty:
    st.warning(f"No profiling data returned for {selected_stage}. Check your BigQuery connection and SQL script.")
    st.stop()

# Target Tables Multi-select based on the loaded dataset
selected_tables = st.sidebar.multiselect(
    "Target Tables", options=df["table_name"].unique(), default=df["table_name"].unique()
)

# Filter the dataframe based on table selection
filtered_df = df[df["table_name"].isin(selected_tables)].copy()

if filtered_df.empty:
    st.warning("No data available for the selected stage and table combination.")
    st.stop()

# --- High-Level KPIs (Dynamic based on selected stage) ---
st.subheader("Pipeline Health Metrics")
col1, col2, col3, col4 = st.columns(4)

if selected_stage == "Raw / Post-Ingestion":
    total_tables = filtered_df["table_name"].nunique()
    total_columns = len(filtered_df)
    pk_count = (
        len(filtered_df[filtered_df["uniqueness_status"].str.contains("PK", na=False)])
        if "uniqueness_status" in filtered_df.columns
        else 0
    )
    columns_with_nulls = (
        len(filtered_df[filtered_df["null_percentage"] > 0]) if "null_percentage" in filtered_df.columns else 0
    )

    col1.metric("Tables Profiled", total_tables)
    col2.metric("Total Columns", total_columns)
    col3.metric("Primary Keys Verified", pk_count)
    col4.metric(
        "Columns with Nulls",
        columns_with_nulls,
        delta=-columns_with_nulls if columns_with_nulls > 0 else None,
        delta_color="inverse",
    )
else:
    # Transformed Anomaly KPIs
    total_tables = filtered_df["table_name"].nunique()
    total_checks = len(filtered_df)
    anomalies_detected = (
        len(filtered_df[filtered_df["status"].str.contains("⚠️", na=False)]) if "status" in filtered_df.columns else 0
    )
    clean_checks = (
        len(filtered_df[filtered_df["status"].str.contains("✅", na=False)]) if "status" in filtered_df.columns else 0
    )

    col1.metric("Models Monitored", total_tables)
    col2.metric("Integrity Gates Run", total_checks)
    col3.metric("Passed Gates", clean_checks)
    col4.metric(
        "Anomalies Detected",
        anomalies_detected,
        delta=-anomalies_detected if anomalies_detected > 0 else None,
        delta_color="inverse",
    )

st.divider()

# --- Detailed Profiling View ---
if selected_stage == "Raw / Post-Ingestion":
    st.subheader("Table Grain & Quality Report")
else:
    st.subheader("Data Anomaly & Fan-Out Prevention Report")


# Universal color styling for both schemas (highlights ⚠️ warnings in soft red and ✅ success in soft green)
def style_health_checks(row):
    color = []
    for col in row.index:
        val = str(row[col])
        cell_style = ""

        # Bold the table name column
        if col == "table_name":
            cell_style += "font-weight: bold; "

        # Health checks coloring
        # if "⚠️" in val or "Duplicate" in val or "Orphaned" in val or "Empty" in val:
        #     cell_style += "background-color: #ffcccc; color: #990000;"
        # elif "✅" in val or "PK" in val or "Clean" in val or "Perfect" in val or "Valid" in val or "Populated" in val:
        #     cell_style += "background-color: #ccffcc; color: #006600;"

        color.append(cell_style)
    return color


# Format column headers to Block (ALL CAPS) style with spaces instead of underscores JUST BEFORE rendering
display_df = filtered_df.copy()
display_df.columns = [str(col).replace("_", " ").upper() for col in display_df.columns]

# Apply the styling to the dataframe
styled_df = display_df.style.apply(style_health_checks, axis=1)

# === INSERT THE CSS SNIPPET HERE ===
st.markdown(
    """
    <style>
    /* This will successfully target standard table headers */
    table th {
        background-color: #1f77b4 !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 14px !important;
        text-align: left !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Render the styled interactive dataframe
st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)

# --- Actionable Insights ---
if selected_stage == "Raw / Post-Ingestion":
    columns_with_nulls = (
        len(filtered_df[filtered_df["null_percentage"] > 0]) if "null_percentage" in filtered_df.columns else 0
    )
    if columns_with_nulls > 0:
        st.error(f"**Attention required:** {columns_with_nulls} column(s) contain null values.")
    else:
        st.success("**Pipeline Green:** All profiled columns are 100% complete.")
else:
    anomalies_detected = (
        len(filtered_df[filtered_df["status"].str.contains("⚠️", na=False)]) if "status" in filtered_df.columns else 0
    )
    if anomalies_detected > 0:
        st.error(
            f"**Fan-Out / Anomaly Alert:** {anomalies_detected} data integrity breach(es) found in transformed models. Review primary keys and foreign key joins."
        )
    else:
        st.success(
            "**Model Green:** All conformed dimensions and facts passed uniqueness and referential integrity checks."
        )
