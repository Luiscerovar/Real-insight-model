
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt

# --- CONTINUING from previous projected_bs, projected_cf calculations ---

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
    net_change_cash = cfo + cfi

    cash = prev_cash + net_change_cash
    fixed_assets = prev_fixed + capex - depreciation
    equity = prev_equity + net_income  # Simplified; ignores dividends/debt changes

    # Append to DataFrames
    projected_cf[year] = [net_income, depreciation, delta_ar, delta_inv, delta_ap, capex, cfo, cfi, net_change_cash]
    projected_bs[year] = [cash, ar, inventory, fixed_assets, ap, 0, equity]  # Debt = 0 simplification

# Format numbers to int for display
projected_cf_display = projected_cf.T.round(0).astype(int)
projected_bs_display = projected_bs.T.round(0).astype(int)

# Show Cash Flow and Balance Sheet projections
st.subheader("Cash Flow Projections")
st.dataframe(projected_cf_display.style.format("{:,.0f}"))

st.subheader("Balance Sheet Projections")
st.dataframe(projected_bs_display.style.format("{:,.0f}"))

# --- Charts ---
st.subheader("📈 Key Financial Charts")

fig, ax = plt.subplots(1, 2, figsize=(12, 4))

# Revenue chart
ax[0].plot(projection_years, projected_is.loc["Revenue"], marker="o", label="Revenue")
ax[0].set_title("Revenue Projection")
ax[0].set_ylabel("Amount")
ax[0].tick_params(axis='x', rotation=45)
ax[0].grid(True)

# Net Income chart
ax[1].plot(projection_years, projected_is.loc["Net Income"], marker="o", color="green", label="Net Income")
ax[1].set_title("Net Income Projection")
ax[1].tick_params(axis='x', rotation=45)
ax[1].grid(True)

st.pyplot(fig)

# --- Valuation: Simple DCF ---
st.subheader("🏦 Basic Valuation via Discounted Cash Flow (DCF)")

discount_rate = st.number_input("Discount Rate (%)", value=10.0)
terminal_growth = st.number_input("Terminal Growth Rate (%)", value=2.0)

# Calculate Free Cash Flow = CFO - CapEx (simplified)
fcf = projected_cf.loc["Cash Flow from Operations"] - projected_cf.loc["CapEx"]

# Discount factors
discount_factors = [(1 + discount_rate / 100) ** (i + 1) for i in range(len(projection_years))]

# Present value of forecast FCF
pv_fcf = [fcf[i] / discount_factors[i] for i in range(len(fcf))]

# Terminal value using Gordon Growth model
terminal_value = fcf[-1] * (1 + terminal_growth / 100) / ((discount_rate - terminal_growth) / 100)
pv_terminal_value = terminal_value / discount_factors[-1]

enterprise_value = sum(pv_fcf) + pv_terminal_value

st.write(f"**Enterprise Value (DCF):** ${enterprise_value:,.0f}")

# --- Download Excel ---
st.subheader("💾 Download Projection Data")

def to_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        projected_is.to_excel(writer, sheet_name="Income Statement")
        projected_cf.to_excel(writer, sheet_name="Cash Flow")
        projected_bs.to_excel(writer, sheet_name="Balance Sheet")
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel()

st.download_button(
    label="Download Excel file",
    data=excel_data,
    file_name="financial_projections.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)