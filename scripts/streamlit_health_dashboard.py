import os
import pandas as pd
import streamlit as st
from google.cloud import bigquery

# 1. Page Configuration
st.set_page_config(page_title="Data Quality Gates", page_icon="🛡️", layout="wide")


# 2. Data Fetching with Caching (Prevents re-running the BQ scan on every click)
@st.cache_data(ttl=3600)
def fetch_profiling_data(sql_file_path: str):
    client = bigquery.Client()

    if not os.path.exists(sql_file_path):
        st.error(f"SQL file not found at: {sql_file_path}")
        return pd.DataFrame()

    with open(sql_file_path, "r") as file:
        script = file.read()

    parent_job = client.query(script)
    parent_job.result()  # Wait for execution

    # Extract the final result set
    for child_job in client.list_jobs(parent_job=parent_job):
        if child_job.destination:
            try:
                df = child_job.to_dataframe()
                if not df.empty:
                    return df
            except Exception:
                continue
    return pd.DataFrame()


# 3. Load Data
sql_path = "scripts/sql/bq_data_profiler.sql"
with st.spinner("Executing Data Profiling Gates in BigQuery..."):
    df = fetch_profiling_data(sql_path)

if df.empty:
    st.warning("No profiling data returned. Check your BigQuery connection and SQL script.")
    st.stop()

# 4. Dashboard UI Elements
st.title("🛡️ Data Observability & Health Profiler")
st.markdown("Automated schema validation, uniqueness checks, and completeness tracking.")

# --- Sidebar Filters ---
st.sidebar.header("Filter Pipeline Data")
selected_tables = st.sidebar.multiselect(
    "Target Tables", options=df["table_name"].unique(), default=df["table_name"].unique()
)

# Filter the dataframe based on selection
filtered_df = df[df["table_name"].isin(selected_tables)]

# --- High-Level KPIs ---
st.subheader("Pipeline Health Metrics")
col1, col2, col3, col4 = st.columns(4)

total_tables = filtered_df["table_name"].nunique()
total_columns = len(filtered_df)
pk_count = len(filtered_df[filtered_df["uniqueness_status"].str.contains("PK")])
columns_with_nulls = len(filtered_df[filtered_df["null_percentage"] > 0])

col1.metric("Tables Profiled", total_tables)
col2.metric("Total Columns", total_columns)
col3.metric("Primary Keys Verified", pk_count)
col4.metric(
    "Columns with Nulls",
    columns_with_nulls,
    delta=-columns_with_nulls if columns_with_nulls > 0 else None,
    delta_color="inverse",
)

st.divider()

# --- Detailed Profiling View ---
st.subheader("Table Grain & Quality Report")


# Apply some color formatting to the dataframe for instant visual feedback
def style_health_checks(row):
    color = []
    for col in row.index:
        if col == "completeness_status" and "⚠️" in str(row[col]):
            color.append("background-color: #ffcccc; color: #990000")  # Light red for null warnings
        elif col == "uniqueness_status" and "PK" in str(row[col]):
            color.append("background-color: #ccffcc; color: #006600")  # Light green for PKs
        else:
            color.append("")
    return color


styled_df = filtered_df.style.apply(style_health_checks, axis=1)

# Render the interactive dataframe
st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)

# --- Actionable Insights ---
if columns_with_nulls > 0:
    st.error(
        f"**Attention required:** {columns_with_nulls} column(s) contain null values. Verify if this is expected business logic."
    )
else:
    st.success("**Pipeline Green:** All profiled columns are 100% complete.")
