
import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.request
import urllib.error
import json
from datetime import date

st.set_page_config(
    page_title="ShopSense | Marketplace Analytics",
    page_icon="🛍️",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

# ---------- PROFESSIONAL STYLING ----------
st.markdown("""
<style>
    .stApp {
        background-color: #f4f7fb;
    }
    [data-testid="stSidebar"] {
        background-color: #142238;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff;
    }
    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #142238;
    }
    .subtitle {
        color: #66758a;
        font-size: 15px;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e4eaf2;
        padding: 18px;
        border-radius: 12px;
    }
    div[data-testid="stMetricLabel"] {
        color: #66758a;
    }
</style>
""", unsafe_allow_html=True)


# ---------- API HELPER ----------
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


# ---------- SIDEBAR ----------
st.sidebar.markdown("# 🛍️ ShopSense")
st.sidebar.caption("MULTI-VENDOR MARKETPLACE")
st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Seller Analysis",
        "Product Analysis",
        "Data Quality & Source",
        "Marketplace Management"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Sales & Inventory Analytics")
st.sidebar.caption("Demonstration application")
st.sidebar.caption("No real payments are processed.")

# ---------- LOAD LIVE DATA ----------
summary, summary_error = get_api_data("/analytics/summary")
products, products_error = get_api_data(
    "/analytics/product-performance"
)
vendors, vendors_error = get_api_data("/vendors/")

if summary is None:
    st.error(
        "Cannot connect to ShopSense API. "
        "Start FastAPI in a separate terminal."
    )
    st.caption(summary_error)
    st.stop()

products = products or []
vendors = vendors or []

product_df = pd.DataFrame(products)
vendor_df = pd.DataFrame(vendors)

if product_df.empty:
    product_df = pd.DataFrame(columns=[
        "product_id", "product_name", "units_sold", "revenue"
    ])

if vendor_df.empty:
    vendor_df = pd.DataFrame(columns=[
        "vendor_id", "business_name", "owner_name",
        "email", "phone", "category", "status"
    ])

# ---------- OVERVIEW ----------
if page == "Overview":
    st.markdown(
        '<div class="main-title">Marketplace Overview</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Monitor sales and product performance.</div>',
        unsafe_allow_html=True
    )
    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Sales Value",
            f"₹{summary['total_revenue']:,.2f}"
        )
    with col2:
        st.metric(
            "Transactions",
            summary["total_transactions"]
        )
    with col3:
        st.metric(
            "Registered Sellers",
            len(vendor_df)
        )
    with col4:
        st.metric(
            "Products",
            summary["total_products"]
        )

    st.success("Connected to live ShopSense data.")

    st.subheader("Sales Performance")

    if not product_df.empty:
        left, right = st.columns(2)

        with left:
            fig = px.bar(
                product_df,
                x="product_name",
                y="revenue",
                title="Revenue by Product",
                labels={
                    "product_name": "Product",
                    "revenue": "Revenue (₹)"
                },
                color="revenue",
                color_continuous_scale="Teal"
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.bar(
                product_df,
                x="product_name",
                y="units_sold",
                title="Units Sold by Product",
                labels={
                    "product_name": "Product",
                    "units_sold": "Units Sold"
                },
                color="units_sold",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Product Performance Summary")
        st.dataframe(product_df, use_container_width=True, hide_index=True)
    else:
        st.info("Add products and transactions to see sales charts.")


# ---------- SELLER ANALYSIS ----------
elif page == "Seller Analysis":
    st.markdown(
        '<div class="main-title">Seller Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown("Explore registered sellers and their status.")

    if not vendor_df.empty:
        status_filter = st.multiselect(
            "Filter by seller status",
            options=sorted(
                vendor_df["status"].dropna().unique().tolist()
            ),
            default=sorted(
                vendor_df["status"].dropna().unique().tolist()
            )
        )

        filtered_vendors = vendor_df[
            vendor_df["status"].isin(status_filter)
        ]

        col1, col2 = st.columns(2)
        col1.metric("Total Sellers", len(vendor_df))
        col2.metric(
            "Active Sellers",
            int((vendor_df["status"] == "active").sum())
        )

        st.subheader("Registered Seller Directory")
        st.dataframe(
            filtered_vendors,
            use_container_width=True,
            hide_index=True
        )

        st.info(
            "Seller revenue rankings require a vendor-level sales "
            "aggregation endpoint. This will be added next."
        )
    else:
        st.info("No sellers have registered yet.")


# ---------- PRODUCT ANALYSIS ----------
elif page == "Product Analysis":
    st.markdown(
        '<div class="main-title">Product Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown("Explore sales, product performance, and categories.")

    if not product_df.empty:
        if not vendor_df.empty:
            category_options = ["All categories"] + sorted(
                vendor_df["category"].dropna().unique().tolist()
            )
        else:
            category_options = ["All categories"]

        selected_category = st.selectbox(
            "Vendor category filter",
            category_options
        )

        if selected_category != "All categories":
            st.caption(
                "This filter applies to vendor categories. "
                "Product category filtering requires product-category "
                "data from the products API."
            )

        col1, col2 = st.columns(2)
        col1.metric(
            "Products in Report",
            len(product_df)
        )
        col2.metric(
            "Units Sold",
            int(product_df["units_sold"].sum())
        )

        fig = px.bar(
            product_df.sort_values("revenue", ascending=False),
            x="product_name",
            y="revenue",
            title="Product Revenue Ranking",
            labels={
                "product_name": "Product",
                "revenue": "Revenue (₹)"
            },
            color="revenue",
            color_continuous_scale="Teal"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Product Details")
        st.dataframe(product_df, use_container_width=True, hide_index=True)
    else:
        st.info("No product performance data is available yet.")


# ---------- DATA QUALITY ----------
elif page == "Data Quality & Source":
    st.markdown(
        '<div class="main-title">Data Quality & Source</div>',
        unsafe_allow_html=True
    )
    st.markdown("Basic quality checks on records currently retrieved.")

    st.subheader("Data Sources")
    st.write("- PostgreSQL database: ShopSense")
    st.write("- Data access: FastAPI REST endpoints")
    st.write("- Dashboard: Streamlit and Plotly")

    checks = []

    for table_name, frame in [
        ("Vendors", vendor_df),
        ("Product Performance", product_df)
    ]:
        checks.append({
            "Dataset": table_name,
            "Rows": len(frame),
            "Duplicate Rows": int(frame.duplicated().sum()),
            "Missing Values": int(frame.isna().sum().sum())
        })

    quality_df = pd.DataFrame(checks)
    st.dataframe(quality_df, use_container_width=True, hide_index=True)

    st.caption(
        "These checks cover the records returned by the API. "
        "They do not constitute a full database audit."
    )


# ---------- MARKETPLACE MANAGEMENT ----------
elif page == "Marketplace Management":
    st.markdown(
        '<div class="main-title">Marketplace Management</div>',
        unsafe_allow_html=True
    )
    st.markdown("Register sellers and view the seller directory.")

    tab_register, tab_vendors = st.tabs([
        "Register Vendor",
        "Registered Vendors"
    ])

    with tab_register:
        with st.form("vendor_registration_form"):
            business_name = st.text_input("Business Name")
            owner_name = st.text_input("Owner Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            category = st.selectbox(
                "Business Category",
                [
                    "Groceries",
                    "Electronics",
                    "Clothing",
                    "Home & Kitchen",
                    "Other"
                ]
            )

            submitted = st.form_submit_button("Register Vendor")

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
                            "Vendor registered successfully! "
                            f"Vendor ID: {result['vendor_id']}"
                        )
                        st.info(f"Status: {result['status']}")
                        st.rerun()
                    except urllib.error.HTTPError as error:
                        detail = error.read().decode("utf-8")
                        if error.code == 400:
                            st.error("This email is already registered.")
                        elif error.code == 422:
                            st.error("Enter a valid email and correct details.")
                        else:
                            st.error(f"Registration failed: {detail}")
                    except Exception as error:
                        st.error(f"Could not register vendor: {error}")

    with tab_vendors:
        st.subheader("Registered Vendors")
        if not vendor_df.empty:
            st.dataframe(
                vendor_df,
                use_container_width=True,
                hide_index=True
            )
            st.caption(f"Total registered vendors: {len(vendor_df)}")
        else:
            st.info("No vendors registered yet.")
