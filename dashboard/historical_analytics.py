
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="ShopSense Historical Analytics",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = (
    BASE_DIR / "data" / "online+retail+ii" / "online_retail_II.xlsx"
)

st.title("ShopSense | Historical Sales Analytics")
st.caption(
    "Historical Online Retail II dataset | 2009–2011 | "
    "GBP (£) | Not live ShopSense transactions"
)

@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path, engine="openpyxl")

    df.columns = df.columns.str.strip()
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    df = df.dropna(subset=["InvoiceDate", "Quantity", "Price"])
    df = df[
        (df["Quantity"] > 0)
        & (df["Price"] > 0)
        & (~df["Invoice"].astype(str).str.startswith("C"))
    ].copy()

    df["Sales"] = df["Quantity"] * df["Price"]
    df["Month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()

    return df

if not DATA_FILE.exists():
    st.error(f"Dataset not found: {DATA_FILE}")
    st.info("Check the Excel filename and the folder spelling.")
    st.stop()

with st.spinner("Loading historical sales data..."):
    df = load_data(str(DATA_FILE))

min_date = df["InvoiceDate"].min().date()
max_date = df["InvoiceDate"].max().date()

st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Invoice date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

countries = sorted(df["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Countries",
    countries,
    default=countries
)

filtered = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["InvoiceDate"].dt.date.between(start_date, end_date)
    ]

if selected_countries:
    filtered = filtered[filtered["Country"].isin(selected_countries)]
else:
    filtered = filtered.iloc[0:0]

total_sales = filtered["Sales"].sum()
invoice_count = filtered["Invoice"].nunique()
units_sold = filtered["Quantity"].sum()
product_count = filtered["StockCode"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales Value", f"£{total_sales:,.2f}")
c2.metric("Distinct Invoices", f"{invoice_count:,}")
c3.metric("Units Sold", f"{units_sold:,.0f}")
c4.metric("Products Sold", f"{product_count:,}")

st.divider()

monthly = (
    filtered.groupby("Month", as_index=False)["Sales"]
    .sum()
    .sort_values("Month")
)

st.subheader("Monthly Sales Trend")
if not monthly.empty:
    fig = px.line(
        monthly,
        x="Month",
        y="Sales",
        markers=True,
        title="Historical monthly revenue",
        labels={"Month": "Month", "Sales": "Sales (£)"}
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No sales found for these filters.")

left, right = st.columns(2)

with left:
    st.subheader("Top 10 Products by Sales")
    top_products = (
        filtered.groupby("Description", as_index=False)
        .agg(Sales=("Sales", "sum"))
        .sort_values("Sales", ascending=False)
        .head(10)
    )

    if not top_products.empty:
        fig_products = px.bar(
            top_products.sort_values("Sales"),
            x="Sales",
            y="Description",
            orientation="h",
            labels={"Sales": "Sales (£)", "Description": "Product"}
        )
        st.plotly_chart(fig_products, use_container_width=True)

with right:
    st.subheader("Sales by Country")
    country_sales = (
        filtered.groupby("Country", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
        .head(10)
    )

    if not country_sales.empty:
        fig_country = px.bar(
            country_sales,
            x="Country",
            y="Sales",
            labels={"Country": "Country", "Sales": "Sales (£)"}
        )
        st.plotly_chart(fig_country, use_container_width=True)

st.subheader("Historical Data Preview")
st.dataframe(
    filtered[
        ["Invoice", "InvoiceDate", "Description", "Quantity",
         "Price", "Sales", "Country"]
    ].head(100),
    use_container_width=True
)
