
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Real Insight Financial Model", layout="wide")

st.title("📊 Real Insight Financial Model")
st.markdown("Upload or input your **historical financials** and set assumptions for projections.")

# --- Tabs for structure ---
tabs = st.tabs(["📁 Historical Data", "⚙️ Assumptions"])

# --- Tab 1: Historical Data ---
with tabs[0]:
    st.header("📁 Upload or Input Historical Financials")

    st.subheader("Income Statement")
    uploaded_is = st.file_uploader("Upload Income Statement (.xlsx, .csv)", key="is_upload")
    if uploaded_is:
        if uploaded_is.name.endswith(".csv"):
            df_is = pd.read_csv(uploaded_is)
        else:
            df_is = pd.read_excel(uploaded_is)
    else:
        # Sample placeholder income statement data
        df_is = pd.DataFrame({
            "Year": [2022, 2023, 2024],
            "Revenue": [100000, 120000, 140000],
            "COGS": [40000, 48000, 56000],
            "Operating Expenses": [30000, 33000, 36000],
            "Net Income": [20000, 26000, 30000]
        })

    df_is = st.data_editor(df_is, num_rows="dynamic", key="income_statement")

    st.subheader("Balance Sheet")
    uploaded_bs = st.file_uploader("Upload Balance Sheet (.xlsx, .csv)", key="bs_upload")
    if uploaded_bs:
        if uploaded_bs.name.endswith(".csv"):
            df_bs = pd.read_csv(uploaded_bs)
        else:
            df_bs = pd.read_excel(uploaded_bs)
    else:
        # Sample placeholder balance sheet data
        df_bs = pd.DataFrame({
            "Year": [2022, 2023, 2024],
            "Cash": [10000, 12000, 15000],
            "Accounts Receivable": [15000, 17000, 20000],
            "Inventory": [10000, 11000, 12000],
            "Fixed Assets": [50000, 52000, 54000],
            "Accounts Payable": [12000, 13000, 14000],
            "Debt": [20000, 18000, 16000],
            "Equity": [53000, 61000, 71000]
        })

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

    st.markdown("These assumptions will be used for projecting P&L, Balance Sheet, and Cash Flow in the next step.")

st.success("✅ Step 1 complete. You can now proceed to build projections.")
