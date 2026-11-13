import streamlit as st
import pandas as pd
import numpy as np

# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="Customer Retention Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Customer Engagement & Product Utilization Analytics")
st.subheader("Customer Retention & Churn Strategy Dashboard")

# ----------------------------------
# LOAD DATA
# ----------------------------------

@st.cache_data
def load_data():
    data = pd.read_csv("Customer Retention Data.csv")

    required_columns = [
        "CustomerId", "CreditScore", "Geography", "Gender",
        "Age", "Tenure", "Balance", "NumOfProducts",
        "HasCrCard", "IsActiveMember", "EstimatedSalary", "Exited"
    ]

    missing = [c for c in required_columns if c not in data.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return data


try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.stop()


# ----------------------------------
# DATA PREPARATION
# ----------------------------------

df["Exited"] = pd.to_numeric(df["Exited"], errors="coerce").fillna(0)
df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce").fillna(0)
df["EstimatedSalary"] = pd.to_numeric(
    df["EstimatedSalary"], errors="coerce"
).fillna(0)

df["IsActiveMember"] = pd.to_numeric(
    df["IsActiveMember"], errors="coerce"
).fillna(0)

df["NumOfProducts"] = pd.to_numeric(
    df["NumOfProducts"], errors="coerce"
).fillna(0)

# Relationship Strength Score: 0-100
df["Relationship Score"] = (
    (df["IsActiveMember"] * 50)
    + (df["NumOfProducts"].clip(0, 4) / 4 * 50)
)

df["Relationship Tier"] = pd.cut(
    df["Relationship Score"],
    bins=[-1, 40, 70, 100],
    labels=["Weak", "Moderate", "Strong"]
)

df["Activity Status"] = df["IsActiveMember"].map({
    0: "Inactive",
    1: "Active"
})

df["Churn Status"] = df["Exited"].map({
    0: "Retained",
    1: "Churned"
})


# ----------------------------------
# SIDEBAR FILTERS
# ----------------------------------

st.sidebar.header("Interactive Dashboard Filters")

geographies = sorted(df["Geography"].dropna().unique().tolist())

selected_geo = st.sidebar.multiselect(
    "Select Geography",
    geographies,
    default=geographies
)

genders = sorted(df["Gender"].dropna().unique().tolist())

selected_gender = st.sidebar.multiselect(
    "Select Gender",
    genders,
    default=genders
)

activity_options = ["Active", "Inactive"]

selected_activity = st.sidebar.multiselect(
    "Customer Engagement",
    activity_options,
    default=activity_options
)

min_products = int(df["NumOfProducts"].min())
max_products = int(df["NumOfProducts"].max())

product_range = st.sidebar.slider(
    "Number of Products",
    min_value=min_products,
    max_value=max_products,
    value=(min_products, max_products)
)

balance_min = float(df["Balance"].min())
balance_max = float(df["Balance"].max())

min_balance = st.sidebar.slider(
    "Minimum Balance",
    min_value=balance_min,
    max_value=balance_max,
    value=balance_min
)

salary_min = float(df["EstimatedSalary"].min())
salary_max = float(df["EstimatedSalary"].max())

max_salary = st.sidebar.slider(
    "Maximum Estimated Salary",
    min_value=salary_min,
    max_value=salary_max,
    value=salary_max
)

filtered = df[
    (df["Geography"].isin(selected_geo))
    & (df["Gender"].isin(selected_gender))
    & (df["Activity Status"].isin(selected_activity))
    & (df["NumOfProducts"].between(
        product_range[0], product_range[1]
    ))
    & (df["Balance"] >= min_balance)
    & (df["EstimatedSalary"] <= max_salary)
].copy()


# ----------------------------------
# MAIN KPI OVERVIEW
# ----------------------------------

st.header("Overall Customer Retention Overview")

total = len(filtered)
churned = int(filtered["Exited"].sum())
retained = total - churned

churn_rate = churned / total * 100 if total else 0
retention_rate = retained / total * 100 if total else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Customers", f"{total:,}")
c2.metric("Retained Customers", f"{retained:,}")
c3.metric("Churned Customers", f"{churned:,}")
c4.metric("Churn Rate", f"{churn_rate:.2f}%")


# ----------------------------------
# FIVE PROJECT KPIs
# ----------------------------------

st.divider()
st.header("Five Key Retention Performance Indicators")

def retention_rate_for(data):
    if len(data) == 0:
        return 0
    return (1 - data["Exited"].mean()) * 100


# Calculate all five KPIs using the complete dataset
active = df[df["IsActiveMember"] == 1]
inactive = df[df["IsActiveMember"] == 0]

active_retention = retention_rate_for(active)
inactive_retention = retention_rate_for(inactive)

engagement_ratio = (
    active_retention / inactive_retention
    if inactive_retention > 0 else None
)

# Product Depth Index
single = df[df["NumOfProducts"] == 1]
multiple = df[df["NumOfProducts"] > 1]

single_retention = retention_rate_for(single)
multiple_retention = retention_rate_for(multiple)

product_depth = (
    multiple_retention / single_retention
    if single_retention > 0 else None
)

# High-Balance Disengagement Rate
median_balance = df["Balance"].median()
high_balance = df[df["Balance"] >= median_balance]

inactive_high_balance = high_balance[
    high_balance["IsActiveMember"] == 0
]

high_balance_disengagement = (
    len(inactive_high_balance) / len(high_balance) * 100
    if len(high_balance) > 0 else None
)

# Credit Card Stickiness
card_holders = df[df["HasCrCard"] == 1]
non_card_holders = df[df["HasCrCard"] == 0]

card_retention = retention_rate_for(card_holders)
non_card_retention = retention_rate_for(non_card_holders)

card_stickiness = (
    card_retention / non_card_retention
    if non_card_retention > 0 else None
)

# Relationship Strength Index
weak = df[df["Relationship Tier"] == "Weak"]
strong = df[df["Relationship Tier"] == "Strong"]

weak_retention = retention_rate_for(weak)
strong_retention = retention_rate_for(strong)

relationship_index = (
    strong_retention / weak_retention
    if weak_retention > 0 else None
)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Engagement Retention Ratio", f"{engagement_ratio:.2f}")
k2.metric("Product Depth Index", f"{product_depth:.2f}")
k3.metric("High-Balance Disengagement", f"{high_balance_disengagement:.2f}%")
k4.metric("Credit Card Stickiness", f"{card_stickiness:.2f}")
k5.metric("Relationship Strength Index", f"{relationship_index:.2f}")

with st.expander("Understand the Five KPIs"):
    st.write("""
    1. Engagement Retention Ratio: Active customer retention divided by inactive customer retention.

    2. Product Depth Index: Multi-product customer retention divided by single-product customer retention.

    3. High-Balance Disengagement Rate: Inactive customers with balance at or above the overall median, divided by all customers at or above that median.

    4. Credit Card Stickiness Score: Credit card holder retention divided by non-holder retention.

    5. Relationship Strength Index: Strong relationship tier retention divided by weak relationship tier retention.
    """)


# ==================================
# MODULE 1: ENGAGEMENT VS CHURN
# ==================================

st.divider()
st.header("Module 1: Engagement vs Churn Overview")

if total:
    activity_churn = (
        filtered.groupby("Activity Status")["Exited"].mean() * 100
    )

    st.subheader("Activity-wise Churn Rate")
    st.bar_chart(activity_churn)

    st.subheader("Geography-wise Churn Rate")
    geo_churn = filtered.groupby("Geography")["Exited"].mean() * 100
    st.bar_chart(geo_churn)

    st.subheader("Gender-wise Churn Rate")
    gender_churn = filtered.groupby("Gender")["Exited"].mean() * 100
    st.bar_chart(gender_churn)
else:
    st.info("No customers match the selected filters.")


# ==================================
# MODULE 2: PRODUCT UTILIZATION
# ==================================

st.divider()
st.header("Module 2: Product Utilization Impact Analysis")

if total:
    product_churn = (
        filtered.groupby("NumOfProducts")["Exited"].mean() * 100
    )

    st.subheader("Product Count vs Churn Rate")
    st.bar_chart(product_churn)

    product_summary = filtered.groupby("NumOfProducts").agg(
        Total_Customers=("CustomerId", "count"),
        Churned_Customers=("Exited", "sum")
    )

    product_summary["Churn_Rate"] = (
        product_summary["Churned_Customers"]
        / product_summary["Total_Customers"] * 100
    )

    st.subheader("Product Utilization Summary")
    st.dataframe(product_summary, width="stretch")


# ==================================
# MODULE 3: HIGH-VALUE DISENGAGED
# ==================================

st.divider()
st.header("Module 3: High-Value Disengaged Customer Detector")

st.write(
    "Identify inactive customers with high balances and "
    "adjustable salary and balance thresholds."
)

detector_balance = st.number_input(
    "Minimum Balance Threshold",
    min_value=0.0,
    value=float(median_balance),
    step=1000.0
)

detector_salary = st.number_input(
    "Maximum Salary Threshold",
    min_value=0.0,
    value=float(df["EstimatedSalary"].median()),
    step=1000.0
)

detector = df[
    (df["IsActiveMember"] == 0)
    & (df["Balance"] >= detector_balance)
    & (df["EstimatedSalary"] <= detector_salary)
].copy()

detector_total = len(detector)
detector_churned = int(detector["Exited"].sum())

detector_churn_rate = (
    detector_churned / detector_total * 100
    if detector_total else 0
)

d1, d2, d3 = st.columns(3)

d1.metric("Disengaged High-Value Customers", f"{detector_total:,}")
d2.metric("Churned Customers", f"{detector_churned:,}")
d3.metric("Segment Churn Rate", f"{detector_churn_rate:.2f}%")

st.subheader("Customer-Level Details")

display_columns = [
    "CustomerId", "Geography", "Gender", "Age",
    "Balance", "EstimatedSalary", "NumOfProducts",
    "Churn Status"
]

st.dataframe(
    detector[display_columns],
    width="stretch"
)

csv_data = detector[display_columns].to_csv(index=False)

st.download_button(
    "Download Disengaged Customer Report",
    data=csv_data,
    file_name="high_value_disengaged_customers.csv",
    mime="text/csv"
)


# ==================================
# MODULE 4: RELATIONSHIP STRENGTH
# ==================================

st.divider()
st.header("Module 4: Retention Strength Scoring Panels")

st.write("""
Relationship Strength Score is a project-specific score based on
customer activity and product usage.

Active status contributes 50 points.
Product usage contributes up to 50 points.
""")

if total:
    tier_summary = filtered.groupby(
        "Relationship Tier",
        observed=False
    ).agg(
        Total_Customers=("CustomerId", "count"),
        Churned_Customers=("Exited", "sum"),
        Average_Score=("Relationship Score", "mean")
    )

    tier_summary["Churn_Rate"] = (
        tier_summary["Churned_Customers"]
        / tier_summary["Total_Customers"].replace(0, np.nan)
        * 100
    ).fillna(0)

    st.subheader("Relationship Tier Performance")
    st.dataframe(tier_summary, width="stretch")

    tier_churn = (
        filtered.groupby("Relationship Tier", observed=False)["Exited"].mean()
        * 100
    )

    st.subheader("Relationship Tier vs Churn Rate")
    st.bar_chart(tier_churn)

    st.subheader("Customer Relationship Scores")

    score_columns = [
        "CustomerId", "IsActiveMember", "NumOfProducts",
        "Relationship Score", "Relationship Tier", "Churn Status"
    ]

    st.dataframe(
        filtered[score_columns].head(500),
        width="stretch"
    )


# ----------------------------------
# FINAL DATA PREVIEW
# ----------------------------------

st.divider()

st.header("Filtered Customer Dataset")
st.write(f"Showing {len(filtered):,} customers after applying dashboard filters.")

st.dataframe(
    filtered.head(100),
    width="stretch"
)

st.caption(
    "Customer Retention Analytics Project | "
    "Data-driven Customer Engagement & Retention Strategy"
)
