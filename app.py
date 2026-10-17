import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Q3 Loyalty Campaign Performance", layout="wide")
st.title("🎰 Q3 Loyalty Campaign ROI & Margin")
st.markdown(
    "Executive summary of Campaign Net Margin and Margin ROI based on player redemptions over the last 30 days."
)


# 2. Load the failsafe data securely
@st.cache_data
def load_data():
    return pd.read_csv("campaign_summary_failsafe.csv")


df = load_data()

# 3. Calculate and display top-level Executive KPIs
total_offers = df["total_offer_amount"].sum()
total_margin = df["total_net_margin"].sum()
overall_roi = total_margin / total_offers if total_offers > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Offer Amount", f"${total_offers:,.0f}")
col2.metric("Total Net Margin", f"${total_margin:,.0f}")
col3.metric("Overall Margin ROI", f"{overall_roi:.2f}x")

st.divider()

# 4. Interactive Elements for the CEO
st.subheader("Performance by Campaign")
campaigns = st.multiselect(
    "Filter by Campaign ID:", options=df["campaign_id"].unique(), default=df["campaign_id"].unique()
)

filtered_df = df[df["campaign_id"].isin(campaigns)]

# 5. Visualizations
chart_col, data_col = st.columns([2, 1])

with chart_col:
    st.bar_chart(data=filtered_df.set_index("campaign_id")["margin_roi"])

with data_col:
    st.dataframe(
        filtered_df[["campaign_id", "margin_roi", "total_net_margin"]], hide_index=True, use_container_width=True
    )
