
import streamlit as st
import pandas as pd
from io import BytesIO

# Must be the first Streamlit command
st.set_page_config(page_title="Real Insight Model", layout="wide")

# Language toggle
language = st.radio("Choose Language / Elija idioma", ["English", "Español"])
def t(en, es):
    return en if language == "English" else es

# Custom CSS styling
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
    }
    .stDownloadButton {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# App title
st.title("📊 Real Insight Financial Model")

projection_type = st.selectbox("Projection Type", ["Yearly", "Monthly"])

if projection_type == "Yearly":
    projection_duration = st.slider("Projection Duration (Years)", 1, 10, 3)
    periods = [str(pd.to_datetime("today").year + i) for i in range(1, projection_duration + 1)]
else:
    projection_duration = st.slider("Projection Duration (Months)", 1, 60, 12)
    start_date = pd.to_datetime("today")
    periods = [(start_date + pd.DateOffset(months=i)).strftime("%b-%Y") for i in range(1, projection_duration + 1)]

st.write(f"Projecting {projection_duration} {projection_type.lower()} period(s):")

tabs = st.tabs(["📁 Historical Data", "⚙️ Assumptions", "📊 Summary"])

# --- Tab 1: Historical Data ---
with tabs[0]:
    st.header(t("📁 Upload or Input Historical Financials", "📁 Ingrese Data histórica"))

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

    st.subheader(t("📋 Input Historical Financials", "📋 Ingrese Data Histórica"))

    st.markdown("#### Income Statement History")
    hist_is = st.data_editor(
        pd.DataFrame({
            "Metric": ["Revenue", "COGS", "Operating Expenses", "Interest", "Taxes", "Net Income"],
            "2022": [0, 0, 0, 0, 0, 0],
            "2023": [0, 0, 0, 0, 0, 0],
        }).set_index("Metric"),
        num_rows="dynamic",
        use_container_width=True
    )

    st.markdown("#### Balance Sheet History")
    hist_bs = st.data_editor(
        pd.DataFrame({
            "Metric": ["Cash", "Accounts Receivable", "Inventory", "Fixed Assets", "Accounts Payable", "Debt", "Equity"],
            "2023": [0, 0, 0, 0, 0, 0, 0],
        }).set_index("Metric"),
        num_rows="dynamic",
        use_container_width=True
    )

    st.markdown("#### Optional: Upload Excel Template")
    uploaded_file = st.file_uploader("Upload your historicals Excel file", type=["xlsx"])
    if uploaded_file:
        uploaded_df = pd.read_excel(uploaded_file, sheet_name=None)
        st.success("File uploaded! You can preview the sheets below.")
        for sheet, data in uploaded_df.items():
            st.markdown(f"**Sheet: {sheet}**")
            st.dataframe(data)

# --- Tab 2: Assumptions ---
with tabs[1]:
    st.subheader(t("Projection Settings", "Configuración de Proyección"))

    freq = st.radio("Projection Frequency", ["Yearly", "Monthly"])
    if freq == "Yearly":
        num_periods = st.slider("Number of Years", 1, 10, 3)
    else:
        num_periods = st.slider("Number of Months", 1, 60, 12)
    
    st.header(t("⚙️ Assumptions for Projections", "⚙️ Supuestos para proyectar"))
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
    st.header(t("📊 Projected Financial Summary", "📊 Resumen de Estados Financieros Proyectados"))

    try:
        import datetime

        if freq == "Yearly":
            start_year = max([int(y) for y in df_is.columns])
            projection_periods = [str(start_year + i) for i in range(1, num_periods + 1)]
        else:
            start = datetime.date(max([int(y) for y in df_is.columns]), 1, 1)
            projection_periods = [(start + datetime.timedelta(days=30 * i)).strftime("%b %Y") for i in range(1, num_periods + 1)]

        projected_is = pd.DataFrame(index=["Revenue", "COGS", "Operating Expenses", "EBIT", "Tax", "Net Income"])

        for i, year in enumerate(projection_years):
            prev_rev = df_is.loc["Revenue"].iloc[-1] if i == 0 else projected_is.loc["Revenue"].iloc[i - 1]
            rev = prev_rev * (1 + revenue_growth / 100)
            cogs = rev * (cogs_pct / 100)
            sga = rev * (sgna_pct / 100)
            ebit = rev - cogs - sga
            tax = ebit * (tax_rate / 100)
            net = ebit - tax
            projected_is[year] = [rev, cogs, sga, ebit, tax, net]

        st.subheader(t("📈 Projected Income Statement", "📈 Estado de Resultados Proyectado"))
        st.dataframe(projected_is.style.format("{:,.0f}"))

        # Cash Flow
        projected_cf = pd.DataFrame(index=[
            "Net Income", "Depreciation", "Change in AR", "Change in Inventory", "Change in AP",
            "CapEx", "Cash Flow from Operations", "Cash Flow from Investing", "Net Change in Cash"
        ])

        projected_bs = pd.DataFrame(index=["Cash", "Accounts Receivable", "Inventory", "Fixed Assets", "Accounts Payable", "Debt", "Equity"])

        for i, year in enumerate(projection_years):
            rev = projected_is.loc["Revenue", year]
            net_income = projected_is.loc["Net Income", year]
            capex = rev * (capex_pct / 100)
            depreciation = capex / depreciation_years

            if i == 0:
                prev_ar = df_bs.loc["Accounts Receivable"].iloc[-1]
                prev_inv = df_bs.loc["Inventory"].iloc[-1]
                prev_ap = df_bs.loc["Accounts Payable"].iloc[-1]
                prev_cash = df_bs.loc["Cash"].iloc[-1]
                prev_fixed = df_bs.loc["Fixed Assets"].iloc[-1]
                prev_equity = df_bs.loc["Equity"].iloc[-1]
            else:
                prev_ar = projected_bs.loc["Accounts Receivable"].iloc[i - 1]
                prev_inv = projected_bs.loc["Inventory"].iloc[i - 1]
                prev_ap = projected_bs.loc["Accounts Payable"].iloc[i - 1]
                prev_cash = projected_bs.loc["Cash"].iloc[i - 1]
                prev_fixed = projected_bs.loc["Fixed Assets"].iloc[i - 1]
                prev_equity = projected_bs.loc["Equity"].iloc[i - 1]

            ar = rev * ar_days / 365
            inventory = rev * inventory_days / 365
            ap = rev * ap_days / 365
            delta_ar = prev_ar - ar
            delta_inv = prev_inv - inventory
            delta_ap = ap - prev_ap
            cfo = net_income + depreciation + delta_ar + delta_inv + delta_ap
            cfi = -capex
            net_cf = cfo + cfi
            cash = prev_cash + net_cf
            fixed_assets = prev_fixed + capex - depreciation
            debt = df_bs.loc["Debt"].iloc[-1]
            equity = prev_equity + net_income

            projected_cf[year] = [net_income, depreciation, delta_ar, delta_inv, delta_ap, -capex, cfo, cfi, net_cf]
            projected_bs[year] = [cash, ar, inventory, fixed_assets, ap, debt, equity]

        st.subheader(t("📘 Projected Balance Sheet", "📘 Balance General Proyectado"))
        st.dataframe(projected_bs.style.format("{:,.0f}"))

        st.subheader(t("💵 Projected Cash Flow Statement", "💵 Flujo de Caja Proyectado"))
        st.dataframe(projected_cf.style.format("{:,.0f}"))

        st.subheader(t("📊 Key Financial Charts", "📊 Gráficos Financieros"))
        st.markdown("### Revenue and Net Income Over Time")
        st.line_chart(projected_is.loc[["Revenue", "Net Income"]].T)

        st.markdown("### Cash Flow from Operations")
        st.bar_chart(projected_cf.loc[["Cash Flow from Operations"]].T)

        st.markdown("### Ending Cash Position")
        st.line_chart(projected_bs.loc[["Cash"]].T)

        st.markdown("### Debt and Equity Over Time")
        st.line_chart(projected_bs.loc[["Debt", "Equity"]].T)

        # Download
        st.subheader("📥 Export Financials to Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            projected_is.to_excel(writer, sheet_name='Income Statement')
            projected_bs.to_excel(writer, sheet_name='Balance Sheet')
            projected_cf.to_excel(writer, sheet_name='Cash Flow')

        st.download_button(
            label="Download Excel File",
            data=output.getvalue(),
            file_name="financial_projections.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Valuation
        st.subheader("💰 Valuation (Discounted Cash Flow)")
        discount_rate = st.number_input("Discount Rate (%)", value=10.0) / 100
        terminal_growth = st.number_input("Terminal Growth Rate (%)", value=2.0) / 100

        cash_flows = projected_cf.loc["Cash Flow from Operations"]
        npv = sum(cash_flows[year] / ((1 + discount_rate) ** (i + 1)) for i, year in enumerate(projection_years))
        terminal_value = (cash_flows[projection_years[-1]] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        terminal_value_pv = terminal_value / ((1 + discount_rate) ** len(projection_years))
        total_value = npv + terminal_value_pv

        st.markdown(f"**NPV of Cash Flows:** ${npv:,.0f}")
        st.markdown(f"**Terminal Value (present value):** ${terminal_value_pv:,.0f}")
        st.markdown(f"**Estimated Business Value:** ${total_value:,.0f}")

    except Exception as e:
        st.warning(f"Could not calculate projections: {e}")
    