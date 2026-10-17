import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Q3 Campaign ROI", layout="wide")
st.title("📊 Q3 Campaign Performance & ROI")
st.markdown("Executive summary of Return on Ad Spend (ROAS) and Conversion Rates over the last 30 days.")


# 2. Load the failsafe data securely
@st.cache_data
def load_data():
    return pd.read_csv("campaign_summary_failsafe.csv")


df = load_data()

# 3. Calculate and display top-level Executive KPIs
total_spend = df["total_spend"].sum()
total_revenue = df["total_revenue"].sum()
overall_roas = total_revenue / total_spend

col1, col2, col3 = st.columns(3)
col1.metric("Total Spend", f"${total_spend:,.0f}")
col2.metric("Total Revenue", f"${total_revenue:,.0f}")
col3.metric("Overall ROAS", f"{overall_roas:.2f}x")

st.divider()

# 4. Interactive Elements for the CEO
st.subheader("Performance by Channel")
channels = st.multiselect(
    "Filter by Channel:", options=df["campaign_channel"].unique(), default=df["campaign_channel"].unique()
)

filtered_df = df[df["campaign_channel"].isin(channels)]

# 5. Visualizations
chart_col, data_col = st.columns([2, 1])

with chart_col:
    st.bar_chart(data=filtered_df.set_index("campaign_channel")["roas"])

with data_col:
    st.dataframe(
        filtered_df[["campaign_channel", "roas", "conversion_rate"]], hide_index=True, use_container_width=True
    )
