import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_loader import load_table


# PAGE CONFIG
st.set_page_config(
    page_title="Car Rental Analytics Dashboard",
    layout="wide"
)

st.title("🚗 Car Rental Analytics Dashboard")
st.markdown(
    """
    Interactive KPI dashboard built using **PostgreSQL + pandas + Streamlit**  
    """
)


# LOAD DATA
#@st.cache_data
def load_data():
    return load_table("analytical_view")

df = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔎 Filters")

segments = sorted(df["segment"].dropna().unique())
selected_segment = st.sidebar.selectbox(
    "Customer Segment",
    options=["All"] + segments
)

if selected_segment != "All":
    df = df[df["segment"] == selected_segment]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_revenue = df["selling_value"].sum()
total_profit = df["profit"].sum()
avg_duration = df["contract_duration"].mean()

profit_margin = (
    (total_profit / total_revenue) * 100
    if total_revenue > 0 else 0
)

# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Revenue", f"{total_revenue:,.0f}")
col2.metric("📈 Total Profit", f"{total_profit:,.0f}")
col3.metric("⏱ Avg Contract Duration", f"{avg_duration:.1f}")
col4.metric("📊 Profit Margin (%)", f"{profit_margin:.2f}")

# --------------------------------------------------
# SEGMENT-LEVEL KPIs
# --------------------------------------------------
st.subheader("📊 Segment Performance")

segment_summary = (
    df.groupby("segment")
    .agg(
        revenue=("selling_value", "sum"),
        profit=("profit", "sum"),
        contracts=("contract_id", "count"),
        avg_duration=("contract_duration", "mean")
    )
    .sort_values("revenue", ascending=False)
)

segment_summary["profit_margin_%"] = (
    segment_summary["profit"] / segment_summary["revenue"] * 100
)

st.dataframe(segment_summary.style.format({
    "revenue": "{:,.0f}",
    "profit": "{:,.0f}",
    "avg_duration": "{:.1f}",
    "profit_margin_%": "{:.2f}"
}))

# --------------------------------------------------
# REVENUE BY SEGMENT (BAR CHART)
# --------------------------------------------------
st.subheader("💰 Revenue by Customer Segment")

fig1, ax1 = plt.subplots()
segment_summary["revenue"].plot(kind="bar", ax=ax1)
ax1.set_xlabel("Segment")
ax1.set_ylabel("Revenue")
ax1.set_title("Revenue by Segment")
plt.tight_layout()

st.pyplot(fig1)

# --------------------------------------------------
# VEHICLE PERFORMANCE & ROI
# --------------------------------------------------
st.subheader("🚘 Vehicle Performance & ROI")

vehicle_perf = (
    df.groupby(["vehicle_id", "desc_vehicle"])
    .agg(
        total_revenue=("selling_value", "sum"),
        purchase_value=("purchase_value", "max"),
        total_profit=("profit", "sum"),
        contracts=("contract_id", "count")
    )
)

vehicle_perf["roi"] = (
    (vehicle_perf["total_revenue"] - vehicle_perf["purchase_value"])
    / vehicle_perf["purchase_value"]
)

top_vehicles = vehicle_perf.sort_values(
    "total_profit", ascending=False
).head(5)

st.markdown("**Top 5 Vehicles by Profit**")
st.dataframe(top_vehicles.style.format({
    "total_revenue": "{:,.0f}",
    "total_profit": "{:,.0f}",
    "roi": "{:.2f}"
}))

# --------------------------------------------------
# PROFIT DISTRIBUTION
# --------------------------------------------------
st.subheader("📉 Profit Distribution")

fig2, ax2 = plt.subplots()
df["profit"].plot(kind="hist", bins=30, ax=ax2)
ax2.set_xlabel("Profit")
ax2.set_ylabel("Frequency")
ax2.set_title("Distribution of Profit per Contract")
plt.tight_layout()

st.pyplot(fig2)

# --------------------------------------------------
# RAW DATA PREVIEW
# --------------------------------------------------
with st.expander("🔍 View Raw Analytics Data"):
    st.dataframe(df)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    """
    ---
    **Tech Stack:** PostgreSQL · SQL · pandas · matplotlib · Streamlit  
    **Use Case:** KPI monitoring & business analytics  
    """
)
