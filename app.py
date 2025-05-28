
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Real Insight Financial Model", layout="wide")

st.title("📊 Real Insight Financial Model")

tabs = st.tabs(["📁 Historical Data", "⚙️ Assumptions", "📊 Summary"])

# --- Tab 1: Historical Data ---
with tabs[0]:
    st.header("📁 Upload or Input Historical Financials (Years as Columns)")

    st.subheader("Income Statement")
    uploaded_is = st.file_uploader("Upload Income Statement (.xlsx, .csv)", key="is_upload")
    if uploaded_is:
        if uploaded_is.name.endswith(".csv"):
            df_is = pd.read_csv(uploaded_is, index_col=0)
        else:
            df_is = pd.read_excel(uploaded_is, index_col=0)
    else:
        df_is = pd.DataFrame({
            "2022": [100000, 40000, 30000, 20000],
            "2023": [120000, 48000, 33000, 26000],
            "2024": [140000, 56000, 36000, 30000]
        }, index=["Revenue", "COGS", "Operating Expenses", "Net Income"])

    df_is = st.data_editor(df_is, num_rows="dynamic", key="income_statement")

    st.subheader("Balance Sheet")
    uploaded_bs = st.file_uploader("Upload Balance Sheet (.xlsx, .csv)", key="bs_upload")
    if uploaded_bs:
        if uploaded_bs.name.endswith(".csv"):
            df_bs = pd.read_csv(uploaded_bs, index_col=0)
        else:
            df_bs = pd.read_excel(uploaded_bs, index_col=0)
    else:
        df_bs = pd.DataFrame({
            "2022": [10000, 15000, 10000, 50000, 12000, 20000, 53000],
            "2023": [12000, 17000, 11000, 52000, 13000, 18000, 61000],
            "2024": [15000, 20000, 12000, 54000, 14000, 16000, 71000]
        }, index=["Cash", "Accounts Receivable", "Inventory", "Fixed Assets",
                  "Accounts Payable", "Debt", "Equity"])

    df_bs = st.data_editor(df_bs, num_rows="dynamic", key="balance_sheet")

# --- Tab 2: Assumptions ---
with tabs[1]:
    st.header("⚙️ Assumptions for Projections")

    col1, col2, col3 = st.columns(3)

    with col1:
        revenue_growth = st.number_input("Revenue Growth (%)", value=10.0)
        cogs_pct = st.number_input("COGS (% of Revenue)", value=40.0)
        sgna_pct = st.number_input("Operating Expenses (% of Revenue)", value=25.0)

    with col2:
        tax_rate = st.number_input("Tax Rate (%)", value=25.0)
        capex_pct = st.number_input("CapEx (% of Revenue)", value=5.0)
        depreciation_years = st.number_input("Useful Life for New Assets (years)", value=5)

    with col3:
        ar_days = st.number_input("Accounts Receivable Days", value=45)
        inventory_days = st.number_input("Inventory Days", value=60)
        ap_days = st.number_input("Accounts Payable Days", value=30)

# --- Tab 3: Summary ---
with tabs[2]:
    st.header("📊 Projected Financial Summary")

    try:
        last_year = max([int(y) for y in df_is.columns])
        projection_years = [str(last_year + i) for i in range(1, 4)]

        projected_is = pd.DataFrame(index=["Revenue", "COGS", "Operating Expenses", "EBIT", "Tax", "Net Income"])

        for i, year in enumerate(projection_years):
            if i == 0:
                prev_rev = df_is.loc["Revenue"].iloc[-1]
            else:
                prev_rev = projected_is.loc["Revenue"].iloc[i - 1]

            rev = prev_rev * (1 + revenue_growth / 100)
            cogs = rev * (cogs_pct / 100)
            sga = rev * (sgna_pct / 100)
            ebit = rev - cogs - sga
            tax = ebit * (tax_rate / 100)
            net = ebit - tax

            projected_is[year] = [rev, cogs, sga, ebit, tax, net]

        st.subheader("📈 Projected Income Statement")
        st.dataframe(projected_is.style.format("{:,.0f}"))
    except Exception as e:
        st.warning(f"Could not calculate projections: {e}")
     
    st.subheader("📘 Projected Balance Sheet")

    projected_bs = pd.DataFrame(index=[
        "Cash", "Accounts Receivable", "Inventory", "Fixed Assets",
        "Accounts Payable", "Debt", "Equity"
    ])

    for i, year in enumerate(projection_years):
        rev = projected_is.loc["Revenue", year]

        ar = rev * ar_days / 365
        inventory = rev * inventory_days / 365
        ap = rev * ap_days / 365
        capex = rev * (capex_pct / 100)
        depreciation = capex / depreciation_years

        if i == 0:
            prev_cash = df_bs.loc["Cash"].iloc[-1]
            prev_fixed = df_bs.loc["Fixed Assets"].iloc[-1]
            prev_equity = df_bs.loc["Equity"].iloc[-1]
        else:
            prev_cash = projected_bs.loc["Cash"].iloc[i - 1]
            prev_fixed = projected_bs.loc["Fixed Assets"].iloc[i - 1]
            prev_equity = projected_bs.loc["Equity"].iloc[i - 1]

        fixed_assets = prev_fixed + capex - depreciation
        net_income = projected_is.loc["Net Income", year]
        equity = prev_equity + net_income  # simplified
        cash = prev_cash + net_income - capex  # simplified
        debt = df_bs.loc["Debt"].iloc[-1]  # assumed constant

        projected_bs[year] = [
            cash, ar, inventory, fixed_assets,
            ap, debt, equity
        ]

    st.dataframe(projected_bs.style.format("{:,.0f}"))

    st.subheader("💵 Projected Cash Flow Statement")

    projected_cf = pd.DataFrame(index=[
        "Net Income",
        "Depreciation",
        "Change in AR",
        "Change in Inventory",
        "Change in AP",
        "CapEx",
        "Cash Flow from Operations",
        "Cash Flow from Investing",
        "Net Change in Cash"
    ])

    for i, year in enumerate(projection_years):
        rev = projected_is.loc["Revenue", year]
        net_income = projected_is.loc["Net Income", year]
        capex = rev * (capex_pct / 100)
        depreciation = capex / depreciation_years

        if i == 0:
            prev_ar = df_bs.loc["Accounts Receivable"].iloc[-1]
            prev_inv = df_bs.loc["Inventory"].iloc[-1]
            prev_ap = df_bs.loc["Accounts Payable"].iloc[-1]
        else:
            prev_ar = projected_bs.loc["Accounts Receivable"].iloc[i - 1]
            prev_inv = projected_bs.loc["Inventory"].iloc[i - 1]
            prev_ap = projected_bs.loc["Accounts Payable"].iloc[i - 1]

        ar = projected_bs.loc["Accounts Receivable", year]
        inv = projected_bs.loc["Inventory", year]
        ap = projected_bs.loc["Accounts Payable", year]

        delta_ar = prev_ar - ar  # negative = cash out
        delta_inv = prev_inv - inv
        delta_ap = ap - prev_ap  # positive = cash in

        cfo = net_income + depreciation + delta_ar + delta_inv + delta_ap
        cfi = -capex
        net_cf = cfo + cfi

        projected_cf[year] = [
            net_income,
            depreciation,
            delta_ar,
            delta_inv,
            delta_ap,
            -capex,
            cfo,
            cfi,
            net_cf
        ]

    st.dataframe(projected_cf.style.format("{:,.0f}"))
    