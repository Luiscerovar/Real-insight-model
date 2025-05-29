
import streamlit as st
import pandas as pd
from io import BytesIO

# --- Page Config ---
st.set_page_config(page_title="Real Insight Model", layout="wide")

# --- Language Toggle ---
language = st.radio("Choose Language / Elija idioma", ["English", "Español"])
def t(en, es): return en if language == "English" else es

# --- App Title ---
st.title("📊 Real Insight Financial Model")

# --- Projection Config ---
projection_type = st.selectbox("Projection Type", ["Yearly", "Monthly"])
if projection_type == "Yearly":
    projection_duration = st.slider("Projection Duration (Years)", 1, 10, 3)
    periods = [str(pd.to_datetime("today").year + i) for i in range(1, projection_duration + 1)]
else:
    projection_duration = st.slider("Projection Duration (Months)", 1, 60, 12)
    start_date = pd.to_datetime("today")
    periods = [(start_date + pd.DateOffset(months=i)).strftime("%b-%Y") for i in range(1, projection_duration + 1)]

st.write(f"Projecting {projection_duration} {projection_type.lower()} period(s):")

# --- Tabs ---
tabs = st.tabs(["📁 Historical Data", "⚙️ Assumptions", "📊 Summary"])

# --- Tab 1: Historical Data ---
with tabs[0]:
    st.subheader(t("Income Statement", "Estado de Resultados"))
    uploaded_is = st.file_uploader("Upload Income Statement (.xlsx, .csv)", key="is_upload")
    if uploaded_is:
        df_is = pd.read_csv(uploaded_is, index_col=0) if uploaded_is.name.endswith(".csv") else pd.read_excel(uploaded_is, index_col=0)
    else:
        df_is = pd.DataFrame({
            "2022": [100000, 40000, 30000, 20000],
            "2023": [120000, 48000, 33000, 26000],
            "2024": [140000, 56000, 36000, 30000]
        }, index=["Revenue", "COGS", "Operating Expenses", "Net Income"])
    df_is = st.data_editor(df_is, num_rows="dynamic", key="income_statement")

    st.subheader(t("Balance Sheet", "Balance General"))
    uploaded_bs = st.file_uploader("Upload Balance Sheet (.xlsx, .csv)", key="bs_upload")
    if uploaded_bs:
        df_bs = pd.read_csv(uploaded_bs, index_col=0) if uploaded_bs.name.endswith(".csv") else pd.read_excel(uploaded_bs, index_col=0)
    else:
        df_bs = pd.DataFrame({
            "2022": [10000, 15000, 10000, 50000, 12000, 20000, 53000],
            "2023": [12000, 17000, 11000, 52000, 13000, 18000, 61000],
            "2024": [15000, 20000, 12000, 54000, 14000, 16000, 71000]
        }, index=["Cash", "Accounts Receivable", "Inventory", "Fixed Assets", "Accounts Payable", "Debt", "Equity"])
    df_bs = st.data_editor(df_bs, num_rows="dynamic", key="balance_sheet")

# --- Tab 2: Assumptions ---
with tabs[1]:
    st.header(t("⚙️ Assumptions for Projections", "⚙️ Supuestos para proyectar"))
    st.markdown("### Revenue Growth Assumptions")

    base_growth = []
    for i, period in enumerate(periods):
        base_growth.append(st.number_input(f"Base Case Revenue Growth (%) - {period}", key=f"base_{i}", value=10.0))

    optimism_factor = st.slider("Optimistic Case Adjustment (%)", -50.0, 100.0, 5.0)
    pessimism_factor = st.slider("Worst Case Adjustment (%)", -50.0, 100.0, -5.0)

    st.markdown("### Cost and Operational Assumptions")
    cogs_pct = st.number_input("COGS (% of Revenue)", value=40.0)
    sgna_pct = st.number_input("Operating Expenses (% of Revenue)", value=25.0)
    tax_rate = st.number_input("Tax Rate (%)", value=25.0)
    capex_pct = st.number_input("CapEx (% of Revenue)", value=5.0)
    depreciation_years = st.number_input("Useful Life for New Assets (years)", value=5)
    ar_days = st.number_input("Accounts Receivable Days", value=45)
    inventory_days = st.number_input("Inventory Days", value=60)
    ap_days = st.number_input("Accounts Payable Days", value=30)

# --- Tab 3: Summary ---
with tabs[2]:
    st.header(t("📊 Projected Financial Summary", "📊 Resumen de Estados Financieros Proyectados"))

    scenarios = {"Base": base_growth, "Optimistic": [x * (1 + optimism_factor / 100) for x in base_growth], "Worst": [x * (1 + pessimism_factor / 100) for x in base_growth]}

    for scenario_name, growth_list in scenarios.items():
        st.subheader(f"📈 {scenario_name} Case Projections")
        projected_is = pd.DataFrame(index=["Revenue", "COGS", "Operating Expenses", "EBIT", "Tax", "Net Income"])

        for i, period in enumerate(periods):
            prev_rev = df_is.loc["Revenue"].iloc[-1] if i == 0 else projected_is.loc["Revenue"].iloc[i - 1]
            rev = prev_rev * (1 + growth_list[i] / 100)
            cogs = rev * cogs_pct / 100
            sga = rev * sgna_pct / 100
            ebit = rev - cogs - sga
            tax = ebit * tax_rate / 100
            net = ebit - tax
            projected_is[period] = [rev, cogs, sga, ebit, tax, net]

        st.dataframe(projected_is.style.format("{:,.0f}"))

        st.line_chart(projected_is.loc[["Revenue", "Net Income"]].T, use_container_width=True)

        # Optional: include DCF valuation for Base Case only
        if scenario_name == "Base":
            st.subheader("💰 Valuation (Discounted Cash Flow)")
            discount_rate = st.number_input("Discount Rate (%)", value=10.0) / 100
            terminal_growth = st.number_input("Terminal Growth Rate (%)", value=2.0) / 100
            cash_flows = projected_is.loc["Net Income"]
            npv = sum(cash_flows[period] / ((1 + discount_rate) ** (i + 1)) for i, period in enumerate(periods))
            terminal_value = (cash_flows[periods[-1]] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
            terminal_value_pv = terminal_value / ((1 + discount_rate) ** len(periods))
            total_value = npv + terminal_value_pv
            st.markdown(f"**NPV of Cash Flows:** ${npv:,.0f}")
            st.markdown(f"**Terminal Value (present value):** ${terminal_value_pv:,.0f}")
            st.markdown(f"**Estimated Business Value:** ${total_value:,.0f}")

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                projected_is.to_excel(writer, sheet_name='Income Statement')
            st.download_button(
                label="📥 Download Excel File",
                data=output.getvalue(),
                file_name="financial_projections.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )