import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Configuration & Custom CSS
st.set_page_config(page_title="Q3 Loyalty Campaign Performance", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    /* Base Theme Overrides */
    .stApp {
        background-color: #121216;
        color: #ffffff;
    }

    /* Custom KPI Cards - Forced equal height and perfect centering */
    .kpi-card {
        background-color: #1e1e24;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        height: 160px; /* Forces identical sizing */
        display: flex;
        flex-direction: column;
        justify-content: center; /* Centers vertically */
        align-items: center; /* Centers horizontally */
        margin-bottom: 20px;
    }
    .kpi-card.gold-border {
        border: 1px solid #c5a059;
    }
    .kpi-card.red-border {
        border: 1px solid #8b0000;
    }
    .kpi-label {
        font-size: 16px;
        color: #e0e0e0;
        margin-bottom: 5px;
        width: 100%;
    }
    .kpi-value-gold {
        font-size: 36px;
        font-weight: bold;
        color: #e5c07b;
        width: 100%;
    }
    .kpi-value-red {
        font-size: 36px;
        font-weight: bold;
        color: #d9534f;
        width: 100%;
    }
    .kpi-subtext {
        font-size: 13px;
        color: #d9534f;
        margin-top: 5px;
        width: 100%;
    }

    /* Header Styling */
    h1 {
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    .sub-header {
        color: #a0a0a0;
        font-size: 18px;
        margin-bottom: 30px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Header Section
st.title("🎰 Q3 LOYALTY CAMPAIGN PERFORMANCE")
st.markdown(
    '<div class="sub-header">Executive summary of Campaign Net Margin and Margin ROI based on player redemptions over the last 30 days.</div>',
    unsafe_allow_html=True,
)


# 3. Load Data
@st.cache_data
def load_data():
    return pd.read_csv("campaign_summary_failsafe.csv")


df = load_data()

total_offers = df["total_offer_amount"].sum()
total_margin = df["total_net_margin"].sum()
overall_roi = total_margin / total_offers if total_offers > 0 else 0

# 4. Custom KPI Row
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card gold-border">
            <div class="kpi-label">Total Offer Amount</div>
            <div class="kpi-value-gold">${total_offers:,.0f}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card red-border">
            <div class="kpi-label">Total Net Margin</div>
            <div class="kpi-value-red">-${abs(total_margin):,.0f}</div>
            <div class="kpi-subtext">▼ -${abs(total_margin):,.0f}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card red-border">
            <div class="kpi-label">Overall Margin ROI</div>
            <div class="kpi-value-red">{overall_roi:.2f}x</div>
            <div class="kpi-subtext">▼ Underperformed</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# 5. Interactive Filter
campaigns = st.multiselect(
    "Filter by Campaign ID:", options=df["campaign_id"].unique(), default=df["campaign_id"].unique()
)

filtered_df = df[df["campaign_id"].isin(campaigns)]

st.markdown("<br>", unsafe_allow_html=True)

# 6. Visualizations Row
chart_col, data_col = st.columns([2, 1])

with chart_col:
    st.markdown("### Campaign Margin ROI Comparison")

    base = (
        alt.Chart(filtered_df)
        .mark_bar(color="#b21f2d")
        .encode(
            y=alt.Y("campaign_id:N", title=None, axis=alt.Axis(labelColor="#e5c07b", labelAngle=0), sort="x"),
            x=alt.X("margin_roi:Q", title="Margin ROI", axis=alt.Axis(labelColor="#e5c07b", titleColor="#e5c07b")),
        )
        .configure_view(strokeWidth=0)
        .configure_axis(
            gridColor="#333333",
            domainColor="#e5c07b",
            tickColor="#e5c07b",
            labelFontSize=14,  # Increases size of the axis numbers/labels
            titleFontSize=16,  # Increases size of the axis title
            labelFontWeight="bold",  # Makes the numbers bold for better contrast
        )
        .properties(height=350)
    )

    st.altair_chart(base, use_container_width=True)

with data_col:
    st.markdown("### Campaign Financial Breakdown")

    display_df = filtered_df[["campaign_id", "margin_roi", "total_net_margin"]].copy()
    display_df.columns = ["Campaign ID", "Margin ROI", "Net Margin"]

    def color_negative_red(val):
        color = "#d9534f" if isinstance(val, (int, float)) and val < 0 else "white"
        return f"color: {color}"

    st.dataframe(
        display_df.style.map(color_negative_red, subset=["Margin ROI", "Net Margin"]).format(
            {"Margin ROI": "{:.2f}", "Net Margin": "${:,.2f}"}
        ),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Campaign ID": st.column_config.Column(alignment="center"),
            "Margin ROI": st.column_config.Column(alignment="center"),
            "Net Margin": st.column_config.Column(alignment="center"),
        },
    )
