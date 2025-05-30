
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Financial Model", layout="wide")

st.title("📊 Financial Projection Tool")

projection_type = st.selectbox("Projection Type", ["Yearly", "Monthly"])

if projection_type == "Yearly":
    projection_duration = st.slider("Projection Duration (Years)", 1, 10, 3)
    periods = [str(pd.to_datetime("today").year + i) for i in range(projection_duration)]
else:
    projection_duration = st.slider("Projection Duration (Months)", 1, 60, 12)
    start_date = pd.to_datetime("today")
    periods = [(start_date + pd.DateOffset(months=i)).strftime("%b-%Y") for i in range(projection_duration)]

st.write(f"Projection Periods: {', '.join(periods)}")

optimism_factor = st.number_input("Optimism Factor (%)", value=20.0)
pessimism_factor = st.number_input("Pessimism Factor (%)", value=-20.0)

# Input for assumptions
st.header("📌 Key Assumptions per Period")
assumption_types = ["Revenue Growth (%)", "COGS (% of Revenue)", "Opex (% of Revenue)", "Tax Rate (%)"]

assumptions_base = {}

for assumption in assumption_types:
    st.subheader(assumption)
    default_value = st.number_input(f"{assumption} - Year 1", value=10.0 if 'Growth' in assumption else 25.0)
    values = [default_value] * projection_duration
    values = st.data_editor(pd.DataFrame({assumption: values}, index=periods), use_container_width=True)
    assumptions_base[assumption] = values[assumption].tolist()

# Prepare scenarios
scenarios = {}
for label, factor in zip(["Base", "Optimistic", "Worst"], [0, optimism_factor / 100, pessimism_factor / 100]):
    assumptions = {}
    for assumption in assumption_types:
        base = assumptions_base[assumption]
        adjusted = [(1 + factor) * x for x in base]
        assumptions[assumption] = adjusted
    scenarios[label] = assumptions

st.header("📈 Projected Income Statements")

projection_results = {}

for label, assumption in scenarios.items():
    income_statement = pd.DataFrame(index=["Revenue", "COGS", "Opex", "EBIT", "Tax", "Net Income"])
    prev_revenue = 100000
    for i, period in enumerate(periods):
        growth = assumption["Revenue Growth (%)"][i] / 100
        cogs_pct = assumption["COGS (% of Revenue)"][i] / 100
        opex_pct = assumption["Opex (% of Revenue)"][i] / 100
        tax_pct = assumption["Tax Rate (%)"][i] / 100

        revenue = prev_revenue * (1 + growth)
        cogs = revenue * cogs_pct
        opex = revenue * opex_pct
        ebit = revenue - cogs - opex
        tax = ebit * tax_pct
        net_income = ebit - tax

        income_statement[period] = [revenue, cogs, opex, ebit, tax, net_income]
        prev_revenue = revenue

    projection_results[label] = income_statement
    st.subheader(f"Scenario: {label}")
    st.dataframe(income_statement.style.format("{:,.0f}"))

    # Charts
    st.line_chart(income_statement.loc[["Revenue", "Net Income"]].T)

# Export to Excel
st.header("📤 Export to Excel")
output = BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    for label, df in projection_results.items():
        df.to_excel(writer, sheet_name=f"{label} IS")

st.download_button(
    label="Download Excel File",
    data=output.getvalue(),
    file_name="financial_projections.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Simple DCF
st.header("💰 Valuation (Discounted Cash Flow)")
discount_rate = st.number_input("Discount Rate (%)", value=10.0) / 100
terminal_growth = st.number_input("Terminal Growth Rate (%)", value=2.0) / 100

selected_scenario = st.selectbox("Select Scenario for Valuation", list(projection_results.keys()))
cash_flows = projection_results[selected_scenario].loc["Net Income"]

npv = sum(cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
terminal_value = (cash_flows.iloc[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
terminal_pv = terminal_value / ((1 + discount_rate) ** len(cash_flows))
enterprise_value = npv + terminal_pv

st.markdown(f"**NPV of Cash Flows:** ${npv:,.0f}")
st.markdown(f"**Terminal Value (present value):** ${terminal_pv:,.0f}")
st.markdown(f"**Estimated Business Value:** ${enterprise_value:,.0f}")
