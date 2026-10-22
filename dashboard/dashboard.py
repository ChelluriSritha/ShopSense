
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.request
import urllib.error
import json

st.set_page_config(
    page_title="ShopSense | Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

# ---------- MODERN WEBSITE DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #f5f7fb;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stSidebar"] {
    background: #111c33;
}
[data-testid="stSidebar"] * {
    color: #edf2ff;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 7px 4px;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}
.brand {
    color: #ffffff;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -1px;
}
.brand span {
    color: #61d6c3;
}
.side-note {
    color: #9baac4;
    font-size: 12px;
}
.page-title {
    color: #17233b;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 3px;
}
.page-subtitle {
    color: #77849a;
    font-size: 14px;
    margin-bottom: 24px;
}
.section-title {
    font-size: 19px;
    font-weight: 700;
    color: #192640;
    padding-top: 12px;
    padding-bottom: 8px;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e7ebf3;
    border-radius: 16px;
    padding: 20px 20px 18px 20px;
    min-height: 125px;
    box-shadow: 0 4px 16px rgba(30, 48, 80, 0.035);
}
.metric-label {
    color: #7b879b;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 12px;
}
.metric-value {
    color: #17233b;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.7px;
}
.metric-foot {
    color: #8995a8;
    font-size: 11px;
    margin-top: 8px;
}
.panel {
    background: #ffffff;
    border: 1px solid #e7ebf3;
    border-radius: 16px;
    padding: 16px;
}
div[data-testid="stForm"] {
    background: white;
    border: 1px solid #e7ebf3;
    border-radius: 14px;
    padding: 20px;
}
.stButton button, .stFormSubmitButton button {
    border-radius: 9px;
    font-weight: 600;
}
[data-testid="stDataFrame"] {
    border: 1px solid #e7ebf3;
    border-radius: 12px;
    overflow: hidden;
}
hr {
    border-color: #e6ebf3;
}
</style>
""", unsafe_allow_html=True)


# ---------- API HELPERS ----------
def get_api_data(endpoint):
    try:
        with urllib.request.urlopen(
            f"{API_URL}{endpoint}", timeout=5
        ) as response:
            return json.loads(response.read().decode()), None
    except Exception as error:
        return None, str(error)


def post_api_data(endpoint, payload):
    request = urllib.request.Request(
        f"{API_URL}{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())


def metric_card(label, value, foot, symbol):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{symbol} &nbsp; {label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-foot">{foot}</div>
    </div>
    """, unsafe_allow_html=True)


def page_heading(title, subtitle):
    st.markdown(
        f'<div class="page-title">{title}</div>'
        f'<div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True
    )


def style_chart(fig, height=330):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#536078", size=12),
        title=dict(font=dict(size=16, color="#192640")),
        margin=dict(l=15, r=15, t=55, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(showgrid=False, linecolor="#e8edf5")
    fig.update_yaxes(gridcolor="#edf1f7", zeroline=False)
    return fig


# ---------- SIDEBAR ----------
st.sidebar.markdown(
    '<div class="brand">Shop<span>Sense</span> 🛍️</div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(
    '<div class="side-note">MULTI-VENDOR MARKETPLACE</div>',
    unsafe_allow_html=True
)
st.sidebar.divider()


page = st.sidebar.radio(
    "WORKSPACE",
    [
        "Overview",
        "Seller Analysis",
        "Product Analysis",
        "Historical Sales Analytics",
        "Data Quality & Source",
        "Marketplace Management"
    ]
)


st.sidebar.divider()
st.sidebar.markdown("**Workspace status**")
st.sidebar.markdown(
    '<div class="side-note">Sales & Inventory Analytics</div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(
    '<div class="side-note">Demo application · No real payments</div>',
    unsafe_allow_html=True
)

if st.sidebar.button("↻ Refresh dashboard", use_container_width=True):
    st.rerun()


# ---------- LOAD DATABASE DATA THROUGH API ----------
summary, summary_error = get_api_data("/analytics/summary")
products, products_error = get_api_data(
    "/analytics/product-performance"
)
vendors, vendors_error = get_api_data("/vendors/")

if summary is None:
    page_heading("ShopSense", "Marketplace analytics workspace")
    st.error("Could not connect to the ShopSense API.")
    st.write("Start the FastAPI server in a separate terminal.")
    st.caption(summary_error)
    st.stop()

products = products or []
vendors = vendors or []

product_df = pd.DataFrame(products)
vendor_df = pd.DataFrame(vendors)

if product_df.empty:
    product_df = pd.DataFrame(
        columns=["product_id", "product_name", "units_sold", "revenue"]
    )

if vendor_df.empty:
    vendor_df = pd.DataFrame(
        columns=[
            "vendor_id", "business_name", "owner_name",
            "email", "phone", "category", "status"
        ]
    )

revenue = float(summary.get("total_revenue", 0) or 0)
transactions = int(summary.get("total_transactions", 0) or 0)
total_products = int(summary.get("total_products", 0) or 0)
total_vendors = len(vendor_df)
active_vendors = (
    int(vendor_df["status"].fillna("").str.lower().eq("active").sum())
    if "status" in vendor_df.columns else 0
)
units_sold = (
    int(pd.to_numeric(product_df["units_sold"], errors="coerce").fillna(0).sum())
    if "units_sold" in product_df.columns else 0
)

# ---------- OVERVIEW ----------
if page == "Overview":
    page_heading(
        "Marketplace Overview",
        "Your business performance at a glance."
    )

    st.markdown("##### KEY PERFORMANCE INDICATORS")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Total sales value", f"₹{revenue:,.2f}",
                    "Recorded transaction revenue", "₹")
    with c2:
        metric_card("Transactions", f"{transactions:,}",
                    "Recorded transaction entries", "↗")
    with c3:
        metric_card("Registered sellers", f"{total_vendors:,}",
                    f"{active_vendors} marked active", "♙")
    with c4:
        metric_card("Products", f"{total_products:,}",
                    f"{units_sold:,} units sold", "▦")

    st.write("")
    st.markdown('<div class="section-title">Sales performance</div>',
                unsafe_allow_html=True)

    left, right = st.columns([1.4, 1])

    with left:
        with st.container(border=True):
            st.markdown("**Revenue by product**")
            if not product_df.empty and "revenue" in product_df.columns:
                chart_df = product_df.copy()
                chart_df["revenue"] = pd.to_numeric(
                    chart_df["revenue"], errors="coerce"
                ).fillna(0)
                chart_df = chart_df.sort_values("revenue", ascending=True)

                fig = px.bar(
                    chart_df,
                    x="revenue",
                    y="product_name",
                    orientation="h",
                    text="revenue",
                    labels={
                        "revenue": "Revenue (₹)",
                        "product_name": ""
                    },
                    color_discrete_sequence=["#3478f6"]
                )
                fig.update_traces(
                    texttemplate="₹%{x:,.0f}",
                    textposition="outside",
                    cliponaxis=False
                )
                fig = style_chart(fig, 340)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Product revenue will appear when data is available.")

    with right:
        with st.container(border=True):
            st.markdown("**Units sold by product**")
            if not product_df.empty and "units_sold" in product_df.columns:
                chart_df = product_df.copy()
                chart_df["units_sold"] = pd.to_numeric(
                    chart_df["units_sold"], errors="coerce"
                ).fillna(0)
                chart_df = chart_df[chart_df["units_sold"] > 0]

                if not chart_df.empty:
                    fig = px.pie(
                        chart_df,
                        names="product_name",
                        values="units_sold",
                        hole=0.65,
                        color_discrete_sequence=[
                            "#3478f6", "#32b8a6", "#f5ad48", "#8b75e8"
                        ]
                    )
                    fig.update_traces(
                        textposition="inside",
                        textinfo="percent+label"
                    )
                    fig = style_chart(fig, 340)
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No units have been sold yet.")
            else:
                st.info("Unit sales data is not available.")

    st.markdown('<div class="section-title">Product performance</div>',
                unsafe_allow_html=True)
    if not product_df.empty:
        display_cols = [
            col for col in [
                "product_id", "product_name", "units_sold", "revenue"
            ] if col in product_df.columns
        ]
        st.dataframe(
            product_df[display_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No product performance records are available.")

    st.caption(
        "Figures are retrieved from your ShopSense API. "
        "A historical revenue trend will be added after transaction-date "
        "data is exposed by the API."
    )


# ---------- SELLER ANALYSIS ----------
elif page == "Seller Analysis":
    page_heading(
        "Seller Analysis",
        "Review seller registrations and marketplace participation."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Registered sellers", f"{total_vendors}",
                    "All seller records", "♙")
    with c2:
        metric_card("Active sellers", f"{active_vendors}",
                    "Status marked active", "✓")
    with c3:
        pending = (
            int(vendor_df["status"].fillna("").str.lower().eq("pending").sum())
            if "status" in vendor_df.columns else 0
        )
        metric_card("Pending sellers", f"{pending}",
                    "Awaiting activation", "◷")

    st.write("")
    if not vendor_df.empty:
        with st.container(border=True):
            st.markdown("**Seller registration status**")
            status_df = (
                vendor_df["status"].fillna("Unknown")
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Sellers")
            )
            fig = px.bar(
                status_df,
                x="Status",
                y="Sellers",
                text="Sellers",
                color="Status",
                color_discrete_sequence=["#3478f6", "#32b8a6", "#f5ad48"]
            )
            fig.update_traces(textposition="outside")
            fig = style_chart(fig, 280)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Seller directory</div>',
                    unsafe_allow_html=True)
        if "status" in vendor_df.columns:
            statuses = sorted(vendor_df["status"].fillna("Unknown").unique())
            selected = st.multiselect(
                "Filter by registration status",
                statuses,
                default=statuses
            )
            filtered = vendor_df[
                vendor_df["status"].fillna("Unknown").isin(selected)
            ]
        else:
            filtered = vendor_df

        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(
            "Seller revenue rankings require a vendor-level sales endpoint."
        )
    else:
        st.info("No sellers have registered yet.")


# ---------- PRODUCT ANALYSIS ----------
elif page == "Product Analysis":
    page_heading(
        "Product Analysis",
        "Understand product sales and identify top performers."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Products in report", f"{len(product_df)}",
                    "Products returned by the API", "▦")
    with c2:
        metric_card("Units sold", f"{units_sold:,}",
                    "Across reported products", "↗")
    with c3:
        metric_card("Product revenue", f"₹{revenue:,.2f}",
                    "Total recorded marketplace revenue", "₹")

    st.write("")
    if not product_df.empty:
        chart_df = product_df.copy()
        chart_df["revenue"] = pd.to_numeric(
            chart_df["revenue"], errors="coerce"
        ).fillna(0)
        chart_df["units_sold"] = pd.to_numeric(
            chart_df["units_sold"], errors="coerce"
        ).fillna(0)

        with st.container(border=True):
            st.markdown("**Product revenue ranking**")
            sort_by = st.selectbox(
                "Rank products by",
                ["Revenue", "Units sold"]
            )
            sort_column = "revenue" if sort_by == "Revenue" else "units_sold"
            ranked = chart_df.sort_values(sort_column, ascending=True)

            fig = px.bar(
                ranked,
                x=sort_column,
                y="product_name",
                orientation="h",
                text=sort_column,
                labels={
                    sort_column: sort_by,
                    "product_name": ""
                },
                color_discrete_sequence=["#32b8a6"]
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig = style_chart(fig, 380)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Product details</div>',
                    unsafe_allow_html=True)
        st.dataframe(chart_df, use_container_width=True, hide_index=True)

        st.caption(
            "Category filtering and stock-level alerts will be connected "
            "once the product and inventory APIs expose those fields."
        )
    else:
        st.info("No product performance data is available yet.")

# ---------- HISTORICAL SALES ANALYTICS ----------
elif page == "Historical Sales Analytics":
    from pathlib import Path

    page_heading(
        "Historical Sales Analytics",
        "Explore historical retail sales trends, products and countries."
    )

    data_file = (
        Path(__file__).resolve().parent.parent
        / "data" / "online+retail+ii" / "online_retail_II.xlsx"
    )

    if not data_file.exists():
        st.error("Historical dataset not found.")
        st.write("Expected file location:")
        st.code(str(data_file))
        st.stop()

    @st.cache_data
    def load_historical_data(file_path):
        sheets = pd.read_excel(
            file_path,
            sheet_name=None,
            engine="openpyxl"
        )

        data = pd.concat(sheets.values(), ignore_index=True)
        data.columns = data.columns.str.strip()

        data["InvoiceDate"] = pd.to_datetime(
            data["InvoiceDate"], errors="coerce"
        )
        data["Quantity"] = pd.to_numeric(
            data["Quantity"], errors="coerce"
        )
        data["Price"] = pd.to_numeric(
            data["Price"], errors="coerce"
        )

        data = data.dropna(
            subset=["InvoiceDate", "Quantity", "Price"]
        )

        data = data[
            (data["Quantity"] > 0)
            & (data["Price"] > 0)
            & (~data["Invoice"].astype(str).str.startswith("C"))
        ].copy()

        data["Sales"] = data["Quantity"] * data["Price"]
        data["Month"] = (
            data["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
        )

        return data

    with st.spinner("Loading historical retail data..."):
        history = load_historical_data(str(data_file))

    if history.empty:
        st.warning("No valid historical sales records were found.")
        st.stop()

    st.caption(
        "Source: Online Retail II | Currency: GBP (£) | "
        "Separate from live ShopSense transactions"
    )

    st.sidebar.subheader("Historical data filters")

    min_date = history["InvoiceDate"].min().date()
    max_date = history["InvoiceDate"].max().date()

    date_range = st.sidebar.date_input(
        "Invoice date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="historical_dates"
    )

    countries = sorted(history["Country"].dropna().unique())

    selected_countries = st.sidebar.multiselect(
        "Select countries",
        options=countries,
        default=["United Kingdom"] if "United Kingdom" in countries else countries[:5],
        key="historical_countries"
    )

    filtered = history.copy()

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            filtered["InvoiceDate"].dt.date.between(
                start_date, end_date
            )
        ]

    filtered = filtered[
        filtered["Country"].isin(selected_countries)
    ]

    total_sales = filtered["Sales"].sum()
    invoice_count = filtered["Invoice"].nunique()
    units = filtered["Quantity"].sum()
    product_count = filtered["StockCode"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Historical sales",
            f"£{total_sales:,.2f}",
            "Value of filtered sales",
            "£"
        )

    with c2:
        metric_card(
            "Invoices",
            f"{invoice_count:,}",
            "Distinct invoice numbers",
            "▤"
        )

    with c3:
        metric_card(
            "Units sold",
            f"{units:,.0f}",
            "Positive quantities only",
            "↗"
        )

    with c4:
        metric_card(
            "Products",
            f"{product_count:,}",
            "Distinct product codes",
            "▦"
        )

    st.write("")

    if filtered.empty:
        st.warning("No records match these filters.")
    else:
        monthly = (
            filtered.groupby("Month", as_index=False)["Sales"]
            .sum()
            .sort_values("Month")
        )

        with st.container(border=True):
            st.markdown("**Monthly sales trend**")

            fig = px.line(
                monthly,
                x="Month",
                y="Sales",
                markers=True,
                labels={
                    "Month": "Month",
                    "Sales": "Sales (£)"
                }
            )
            fig = style_chart(fig, 380)
            st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)

        with left:
            with st.container(border=True):
                st.markdown("**Top 10 products by sales**")

                top_products = (
                    filtered.groupby("Description", as_index=False)
                    .agg(Sales=("Sales", "sum"))
                    .sort_values("Sales", ascending=False)
                    .head(10)
                    .sort_values("Sales")
                )

                fig = px.bar(
                    top_products,
                    x="Sales",
                    y="Description",
                    orientation="h",
                    labels={
                        "Sales": "Sales (£)",
                        "Description": "Product"
                    },
                    color_discrete_sequence=["#3478f6"]
                )
                fig = style_chart(fig, 400)
                st.plotly_chart(fig, use_container_width=True)

        with right:
            with st.container(border=True):
                st.markdown("**Top 10 countries by sales**")

                country_sales = (
                    filtered.groupby("Country", as_index=False)
                    .agg(Sales=("Sales", "sum"))
                    .sort_values("Sales", ascending=False)
                    .head(10)
                    .sort_values("Sales")
                )

                fig = px.bar(
                    country_sales,
                    x="Sales",
                    y="Country",
                    orientation="h",
                    labels={
                        "Sales": "Sales (£)",
                        "Country": "Country"
                    },
                    color_discrete_sequence=["#32b8a6"]
                )
                fig = style_chart(fig, 400)
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("View historical sales records"):
            preview_cols = [
                "Invoice", "InvoiceDate", "Description",
                "Quantity", "Price", "Sales", "Country"
            ]
            st.dataframe(
                filtered[preview_cols].head(100),
                use_container_width=True,
                hide_index=True
            )



# ---------- DATA QUALITY & SOURCE ----------
elif page == "Data Quality & Source":
    page_heading(
        "Data Quality & Source",
        "Review the records received from the ShopSense API."
    )

    st.markdown('<div class="section-title">Data connections</div>',
                unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        metric_card("Database", "PostgreSQL",
                    "ShopSense database", "▤")
    with b:
        metric_card("API", "FastAPI",
                    "REST endpoints", "↔")
    with c:
        metric_card("Charts", "Plotly",
                    "Interactive visualizations", "▥")

    st.write("")
    checks = []
    for name, frame in [
        ("Vendors", vendor_df),
        ("Product performance", product_df)
    ]:
        checks.append({
            "Dataset": name,
            "Rows received": len(frame),
            "Duplicate rows": int(frame.duplicated().sum()),
            "Missing values": int(frame.isna().sum().sum())
        })

    quality_df = pd.DataFrame(checks)
    with st.container(border=True):
        st.markdown("**Data quality checks**")
        st.dataframe(quality_df, use_container_width=True, hide_index=True)

    st.info(
        "These checks cover only the data returned by the current API "
        "endpoints. They are not a complete database audit."
    )

    with st.container(border=True):
        st.markdown("**Data flow**")
        st.markdown(
            "PostgreSQL database → FastAPI → Streamlit dashboard → Plotly charts"
        )
        st.caption(
            "The dashboard uses live API responses when the backend is running."
        )


# ---------- MARKETPLACE MANAGEMENT ----------
elif page == "Marketplace Management":
    page_heading(
        "Marketplace Management",
        "Register sellers and manage the seller directory."
    )

    tab_register, tab_directory = st.tabs(
        ["＋ Register seller", "▤ Seller directory"]
    )

    with tab_register:
        st.markdown("**Seller onboarding**")
        st.caption("Enter business details to register a new marketplace seller.")

        with st.form("vendor_registration_form"):
            business_name = st.text_input("Business name")
            owner_name = st.text_input("Owner name")
            email = st.text_input("Email address")
            phone = st.text_input("Phone number")
            category = st.selectbox(
                "Business category",
                [
                    "Groceries", "Electronics", "Clothing",
                    "Home & Kitchen", "Other"
                ]
            )
            submitted = st.form_submit_button(
                "Register seller",
                use_container_width=True
            )

            if submitted:
                if not all([
                    business_name.strip(),
                    owner_name.strip(),
                    email.strip(),
                    phone.strip()
                ]):
                    st.error("Please fill in all required fields.")
                else:
                    payload = {
                        "business_name": business_name.strip(),
                        "owner_name": owner_name.strip(),
                        "email": email.strip(),
                        "phone": phone.strip(),
                        "category": category
                    }
                    try:
                        result = post_api_data("/vendors/", payload)
                        st.success(
                            f"Seller registered successfully. "
                            f"ID: {result['vendor_id']}"
                        )
                        st.info(f"Registration status: {result['status']}")
                        st.rerun()
                    except urllib.error.HTTPError as error:
                        detail = error.read().decode("utf-8")
                        if error.code == 400:
                            st.error("This email may already be registered.")
                        elif error.code == 422:
                            st.error("Please check the email and entered details.")
                        else:
                            st.error(f"Registration failed: {detail}")
                    except Exception as error:
                        st.error(f"Could not register seller: {error}")

    with tab_directory:
        st.markdown("**Registered sellers**")
        if not vendor_df.empty:
            st.dataframe(
                vendor_df,
                use_container_width=True,
                hide_index=True
            )
            st.caption(f"{len(vendor_df)} seller records retrieved.")
        else:
            st.info("No sellers registered yet.")

st.sidebar.divider()
st.sidebar.caption("ShopSense · Marketplace Analytics")
st.sidebar.caption("Local demonstration build")
