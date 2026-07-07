"""
Business KPI Dashboard
-----------------------
A Streamlit + Plotly dashboard showing Revenue, Profit, Customer Growth,
Monthly Trends, and Customer Feedback Sentiment (TextBlob), with interactive
filters for Date Range, Region, and Product.

Run with:
    streamlit run app.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Business KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------
@st.cache_data
def load_data(path="data/sales_data.csv"):
    df = pd.read_csv(path, parse_dates=["Date"])
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Year"] = df["Date"].dt.year
    return df


@st.cache_data
def get_sentiment(text):
    """Return polarity score (-1 to 1) and label using TextBlob."""
    polarity = TextBlob(str(text)).sentiment.polarity
    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
    return polarity, label


df = load_data()

# ----------------------------------------------------------------------
# SIDEBAR - INTERACTIVE FILTERS
# ----------------------------------------------------------------------
st.sidebar.title("🔎 Filters")

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

regions = st.sidebar.multiselect(
    "Region", options=sorted(df["Region"].unique()), default=sorted(df["Region"].unique())
)

products = st.sidebar.multiselect(
    "Product", options=sorted(df["Product"].unique()), default=sorted(df["Product"].unique())
)

st.sidebar.markdown("---")
st.sidebar.caption("Data source: data/sales_data.csv (sample generated data)")

# Handle single-date edge case from date_input
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# ----------------------------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------------------------
mask = (
    (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
    & (df["Region"].isin(regions))
    & (df["Product"].isin(products))
)
fdf = df.loc[mask].copy()

if fdf.empty:
    st.warning("No data matches the selected filters. Please broaden your selection.")
    st.stop()

# ----------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------
st.title("📊 Business KPI Dashboard")
st.caption("Revenue, Profit, Customer Growth & Trends — filter using the sidebar")

# ----------------------------------------------------------------------
# KPI CALCULATIONS
# ----------------------------------------------------------------------
total_revenue = fdf["Revenue"].sum()
total_profit = fdf["Profit"].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
total_customers = fdf["CustomerID"].nunique()

# Customer growth: new customers per month vs first appearance in full dataset
first_seen = df.groupby("CustomerID")["Month"].min().rename("FirstMonth")
fdf_growth = fdf.join(first_seen, on="CustomerID")
monthly_new_customers = (
    fdf_growth[fdf_growth["Month"] == fdf_growth["FirstMonth"]]
    .groupby("Month")["CustomerID"].nunique()
)

# Growth % vs previous period (compare last 2 months of filtered range)
monthly_customers_active = fdf.groupby("Month")["CustomerID"].nunique().sort_index()
if len(monthly_customers_active) >= 2:
    prev, curr = monthly_customers_active.iloc[-2], monthly_customers_active.iloc[-1]
    cust_growth_pct = ((curr - prev) / prev * 100) if prev else 0
else:
    cust_growth_pct = 0

# ----------------------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
col2.metric("📈 Total Profit", f"${total_profit:,.0f}", f"{profit_margin:.1f}% margin")
col3.metric("👥 Active Customers", f"{total_customers:,}", f"{cust_growth_pct:+.1f}% MoM")
col4.metric("🧾 Total Orders", f"{len(fdf):,}")

st.markdown("---")

# ----------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Monthly Trends", "🌍 Region & Product Breakdown", "👥 Customer Growth", "💬 Feedback Sentiment"]
)

# ---- TAB 1: Monthly Trends ----
with tab1:
    st.subheader("Revenue & Profit Trends Over Time")

    monthly = fdf.groupby("Month").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Revenue", "count"),
    ).reset_index()

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Revenue"], mode="lines+markers",
        name="Revenue", line=dict(color="#2E86DE", width=3)
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Profit"], mode="lines+markers",
        name="Profit", line=dict(color="#10AC84", width=3)
    ))
    fig_trend.update_layout(
        xaxis_title="Month", yaxis_title="Amount ($)",
        hovermode="x unified", template="plotly_white", height=450,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    fig_orders = px.bar(
        monthly, x="Month", y="Orders", title="Monthly Order Volume",
        template="plotly_white", color_discrete_sequence=["#8E44AD"],
    )
    fig_orders.update_layout(height=350)
    st.plotly_chart(fig_orders, use_container_width=True)

# ---- TAB 2: Region & Product Breakdown ----
with tab2:
    st.subheader("Performance by Region & Product")

    c1, c2 = st.columns(2)
    with c1:
        region_rev = fdf.groupby("Region")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
        fig_region = px.bar(
            region_rev, x="Region", y="Revenue", color="Region",
            title="Revenue by Region", template="plotly_white",
        )
        st.plotly_chart(fig_region, use_container_width=True)

    with c2:
        product_rev = fdf.groupby("Product")["Revenue"].sum().reset_index()
        fig_product = px.pie(
            product_rev, names="Product", values="Revenue",
            title="Revenue Share by Product", hole=0.4,
            template="plotly_white",
        )
        st.plotly_chart(fig_product, use_container_width=True)

    profit_by_product = fdf.groupby("Product").agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum")
    ).reset_index()
    profit_by_product["Margin %"] = (profit_by_product["Profit"] / profit_by_product["Revenue"] * 100).round(1)
    fig_margin = px.bar(
        profit_by_product, x="Product", y="Margin %", title="Profit Margin % by Product",
        template="plotly_white", color="Margin %", color_continuous_scale="Greens",
    )
    st.plotly_chart(fig_margin, use_container_width=True)

# ---- TAB 3: Customer Growth ----
with tab3:
    st.subheader("Customer Growth Over Time")

    growth_df = monthly_new_customers.reset_index()
    growth_df.columns = ["Month", "New Customers"]
    growth_df["Cumulative Customers"] = growth_df["New Customers"].cumsum()

    fig_new = px.bar(
        growth_df, x="Month", y="New Customers", title="New Customers Acquired per Month",
        template="plotly_white", color_discrete_sequence=["#F39C12"],
    )
    st.plotly_chart(fig_new, use_container_width=True)

    fig_cum = px.area(
        growth_df, x="Month", y="Cumulative Customers", title="Cumulative Customer Growth",
        template="plotly_white", color_discrete_sequence=["#2E86DE"],
    )
    st.plotly_chart(fig_cum, use_container_width=True)

    active_df = monthly_customers_active.reset_index()
    active_df.columns = ["Month", "Active Customers"]
    fig_active = px.line(
        active_df, x="Month", y="Active Customers", markers=True,
        title="Active (Purchasing) Customers per Month", template="plotly_white",
    )
    st.plotly_chart(fig_active, use_container_width=True)

# ---- TAB 4: Feedback Sentiment (TextBlob) ----
with tab4:
    st.subheader("Customer Feedback Sentiment Analysis")
    st.caption("Sentiment computed using TextBlob polarity scoring on customer feedback text.")

    sentiment_results = fdf["Feedback"].apply(get_sentiment)
    fdf["Polarity"] = sentiment_results.apply(lambda x: x[0])
    fdf["Sentiment"] = sentiment_results.apply(lambda x: x[1])

    c1, c2 = st.columns([1, 2])
    with c1:
        sentiment_counts = fdf["Sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
        fig_sent = px.pie(
            sentiment_counts, names="Sentiment", values="Count",
            title="Feedback Sentiment Distribution",
            color="Sentiment",
            color_discrete_map={"Positive": "#10AC84", "Neutral": "#F39C12", "Negative": "#EE5253"},
        )
        st.plotly_chart(fig_sent, use_container_width=True)

    with c2:
        sentiment_trend = fdf.groupby(["Month", "Sentiment"]).size().reset_index(name="Count")
        fig_sent_trend = px.bar(
            sentiment_trend, x="Month", y="Count", color="Sentiment",
            title="Sentiment Trend Over Time", template="plotly_white",
            color_discrete_map={"Positive": "#10AC84", "Neutral": "#F39C12", "Negative": "#EE5253"},
        )
        st.plotly_chart(fig_sent_trend, use_container_width=True)

    st.markdown("#### Sample Feedback")
    st.dataframe(
        fdf[["Date", "Region", "Product", "Feedback", "Polarity", "Sentiment"]]
        .sort_values("Date", ascending=False)
        .head(20),
        use_container_width=True,
    )

# ----------------------------------------------------------------------
# RAW DATA (optional expand)
# ----------------------------------------------------------------------
with st.expander("🔍 View Filtered Raw Data"):
    st.dataframe(fdf, use_container_width=True)
    st.download_button(
        "Download Filtered Data as CSV",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="filtered_kpi_data.csv",
        mime="text/csv",
    )
