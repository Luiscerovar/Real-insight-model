
import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="Financial Model", layout="wide")

# Initialize session state
if "years" not in st.session_state:
    st.session_state["years"] = 5

if "historical_data" not in st.session_state:
    st.session_state["historical_data"] = pd.DataFrame({
        "Year": [datetime.now().year - i for i in range(1, 4)][::-1],
        "Revenue": [100000, 120000, 140000],
        "COGS": [40000, 48000, 56000],
        "OPEX": [30000, 32000, 34000]
    })

# Sidebar controls
st.sidebar.header("Settings")
st.session_state["years"] = st.sidebar.slider("Projection Duration (Years)", 1, 10, st.session_state["years"])

# Tabs
pages = st.tabs(["Historical Data", "Assumptions", "Projections", "Charts", "Valuation"])

# --- Tab 1: Historical Data ---
with pages[0]:
    st.subheader("Historical Financial Data")
    # Transpose for years as columns
    edited = st.data_editor(st.session_state["historical_data"].set_index("Year").T)
    st.session_state["historical_data"] = edited.T.reset_index().rename(columns={"index": "Year"})

# --- Tab 2: Assumptions ---
with pages[1]:
    st.subheader("Key Assumptions (Yearly, Scenario-Based)")
    scenarios = ["Base", "Optimistic", "Worst"]
    assumption_names = [
        "Revenue Growth (%)", "COGS (% of Revenue)", "OPEX (% of Revenue)",
        "Tax Rate (%)", "Depreciation (% of Revenue)", "CapEx (% of Revenue)", "Working Capital (% of Revenue)"
    ]
    assumptions = {}

    for name in assumption_names:
        assumptions[name] = {}
        with st.expander(name):
            for scenario in scenarios:
                same = st.checkbox(f"Same every year ({scenario})", value=True, key=f"same_{name}_{scenario}")
                values = []
                for year in range(1, st.session_state["years"] + 1):
                    if year == 1 or not same:
                        val = st.number_input(f"{scenario} - Year {year}", value=10.0, step=1.0, key=f"{name}_{scenario}_{year}")
                    else:
                        val = values[0]
                    values.append(val)
                assumptions[name][scenario] = values

# --- Tab 3: Projections ---
with pages[2]:
    st.subheader("Projections")
    projection_data = {}

    for scenario in scenarios:
        revenue = [st.session_state["historical_data"].iloc[-1]["Revenue"]]
        for g in assumptions["Revenue Growth (%)"][scenario]:
            revenue.append(revenue[-1] * (1 + g / 100))
        revenue = revenue[1:]

        cogs = [r * assumptions["COGS (% of Revenue)"][scenario][i] / 100 for i, r in enumerate(revenue)]
        opex = [r * assumptions["OPEX (% of Revenue)"][scenario][i] / 100 for i, r in enumerate(revenue)]
        depreciation = [r * assumptions["Depreciation (% of Revenue)"][scenario][i] / 100 for i, r in enumerate(revenue)]
        capex = [r * assumptions["CapEx (% of Revenue)"][scenario][i] / 100 for i, r in enumerate(revenue)]
        working_capital = [r * assumptions["Working Capital (% of Revenue)"][scenario][i] / 100 for i, r in enumerate(revenue)]

        ebit = [revenue[i] - cogs[i] - opex[i] - depreciation[i] for i in range(st.session_state["years"])]
        tax = [ebit[i] * assumptions["Tax Rate (%)"][scenario][i] / 100 for i in range(st.session_state["years"])]
        net_income = [ebit[i] - tax[i] for i in range(st.session_state["years"])]
        fcf = [net_income[i] + depreciation[i] - capex[i] - working_capital[i] for i in range(st.session_state["years"])]

        assets = np.cumsum([capex[i] for i in range(st.session_state["years"])])
        liabilities = np.cumsum([working_capital[i] * 0.5 for i in range(st.session_state["years"])])
        equity = np.cumsum(net_income)

        df = pd.DataFrame({
            "Year": [datetime.now().year + i for i in range(1, st.session_state["years"] + 1)],
            "Revenue": revenue,
            "COGS": cogs,
            "OPEX": opex,
            "EBIT": ebit,
            "Net Income": net_income,
            "FCF": fcf,
            "Assets": assets,
            "Liabilities": liabilities,
            "Equity": equity
        })

        projection_data[scenario] = df
        st.write(f"### {scenario} Scenario")
        st.dataframe(df.set_index("Year").T)

# --- Tab 4: Charts ---
with pages[3]:
    st.subheader("Charts")
    metric = st.selectbox("Select Metric", ["Revenue", "EBIT", "Net Income", "FCF"])
    chart_df = pd.DataFrame({
        scenario: projection_data[scenario][metric] for scenario in scenarios
    })
    chart_df.index = projection_data[scenarios[0]]["Year"]
    st.line_chart(chart_df)

# --- Tab 5: Valuation ---
with pages[4]:
    st.subheader("Valuation (Discounted Cash Flow)")
    discount_rate = st.number_input("Discount Rate (%)", value=10.0, step=0.5)
    valuations = {}
    for scenario in scenarios:
        fcf = projection_data[scenario]["FCF"]
        discounted_fcf = [fcf[i] / (1 + discount_rate / 100) ** (i + 1) for i in range(len(fcf))]
        valuation = sum(discounted_fcf)
        valuations[scenario] = valuation
        st.metric(f"{scenario} Valuation", f"${valuation:,.0f}")

    if st.button("Download Projections to Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for scenario in scenarios:
                projection_data[scenario].to_excel(writer, sheet_name=scenario, index=False)
        st.download_button(
            label="Download Excel File",
            data=output.getvalue(),
            file_name="financial_model.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )