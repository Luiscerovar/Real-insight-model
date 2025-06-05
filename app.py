
import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="Financial Model", layout="wide")

# Initialize session state
if "years" not in st.session_state:
    st.session_state["years"] = 5


# Sidebar controls
st.sidebar.header("Settings")
st.session_state["years"] = st.sidebar.slider("Projection Duration (Years)", 1, 10, st.session_state["years"])


# Define tabs
tabs = st.tabs([
    "Historical Data", "Assumptions", "Depreciation & Amortization", "Debt",
    "Projections", "Charts", "Valuation"
])

# --- Tab 1: Historical Data ---
with tabs[0]:
    st.subheader("Historical Financial Data")

    input_cols = [
        "Ingresos", "Costo de Ventas", "Gastos Administración", "Gastos Ventas",
        "Depreciación", "Amortización", "Otros Ingresos No Operativos", "Otros Gastos No Operativos",
        "Resultado Financiero Neto", "Participación de Trabajadores", "Impuestos"
    ]

    if "historical_data" not in st.session_state or st.session_state["historical_data"].empty:
        current_year = datetime.now().year
        st.session_state["historical_data"] = pd.DataFrame({
            "Year": [current_year - i for i in reversed(range(3))],
            "Ingresos": [100000, 120000, 140000],
            "Costo de Ventas": [40000, 48000, 56000],
            "Gastos Administración": [15000, 16000, 17000],
            "Gastos Ventas": [15000, 16000, 17000],
            "Depreciación": [5000, 6000, 7000],
            "Amortización": [2000, 2500, 3000],
            "Otros Ingresos No Operativos": [1000, 1100, 1200],
            "Otros Gastos No Operativos": [500, 600, 700],
            "Resultado Financiero Neto": [1000, 1200, 1500],
            "Participación de Trabajadores": [2000, 2200, 2500],
            "Impuestos": [5000, 5500, 6000]
        })

    df_inputs = st.data_editor(
        st.session_state["historical_data"][["Year"] + input_cols].set_index("Year"),
        num_rows="dynamic",
        use_container_width=True
    )

    st.session_state["historical_data"].update(df_inputs.reset_index())

    df_hist = st.session_state["historical_data"]
    ingresos = df_hist["Ingresos"]
    costo_ventas = df_hist["Costo de Ventas"]
    gastos_admin = df_hist["Gastos Administración"]
    gastos_ventas = df_hist["Gastos Ventas"]
    depreciacion = df_hist["Depreciación"]
    amortizacion = df_hist["Amortización"]
    otros_ingresos = df_hist["Otros Ingresos No Operativos"]
    otros_gastos = df_hist["Otros Gastos No Operativos"]
    resultado_financiero = df_hist["Resultado Financiero Neto"]
    participacion_trabajadores = df_hist["Participación de Trabajadores"]
    impuestos = df_hist["Impuestos"]

    utilidad_bruta = ingresos - costo_ventas
    ebitda = utilidad_bruta - gastos_admin - gastos_ventas
    ebit = ebitda - depreciacion - amortizacion
    ebt = ebit + otros_ingresos - otros_gastos + resultado_financiero
    utilidad_neta = ebt - participacion_trabajadores - impuestos

    income_statement = pd.DataFrame({
        "Ingresos": ingresos,
        "Costo de Ventas": costo_ventas,
        "UTILIDAD BRUTA": utilidad_bruta,
        "Gastos Administración": gastos_admin,
        "Gastos Ventas": gastos_ventas,
        "UTILIDAD ANTES DE DEP Y AMORT (EBITDA)": ebitda,
        "Depreciación": depreciacion,
        "Amortización": amortizacion,
        "UTILIDAD OPERATIVA (EBIT)": ebit,
        "Otros Ingresos No Operativos": otros_ingresos,
        "Otros Gastos No Operativos": otros_gastos,
        "Resultado Financiero Neto": resultado_financiero,
        "UTILIDAD ANTES DE IMPUESTOS Y PARTICIPACIÓN TRABAJADORES (EBT)": ebt,
        "Participación de Trabajadores": participacion_trabajadores,
        "Impuestos": impuestos,
        "UTILIDAD NETA": utilidad_neta
    }, index=df_hist["Year"]).T

    st.markdown("### Income Statement (Calculated Fields & Inputs)")
    st.dataframe(income_statement)

    # BALANCE SHEET SECTION
    st.markdown("### Balance Sheet (Inputs & Calculated Totals)")

    historical_years = df_hist["Year"].tolist()
    num_years = len(historical_years)

    bs_cols = [
        "Cash", "Accounts Receivable", "Inventory", "Other Current Assets",
        "Net PPE", "Net Intangibles", "Other Non-Current Assets",
        "Accounts Payable", "Short-Term Debt", "Other Current Liabilities",
        "Long-Term Debt", "Other Non-Current Liabilities",
        "Retained Earnings", "Other Equity"
    ]

    if "balance_sheet_inputs" not in st.session_state or st.session_state["balance_sheet_inputs"].empty:
        st.session_state["balance_sheet_inputs"] = pd.DataFrame({
            "Year": historical_years,
            "Cash": [10000.0] * num_years,
            "Accounts Receivable": [8000.0] * num_years,
            "Inventory": [7000.0] * num_years,
            "Other Current Assets": [3000.0] * num_years,
            "Net PPE": [25000.0] * num_years,
            "Net Intangibles": [5000.0] * num_years,
            "Other Non-Current Assets": [2000.0] * num_years,
            "Accounts Payable": [6000.0] * num_years,
            "Short-Term Debt": [4000.0] * num_years,
            "Other Current Liabilities": [3000.0] * num_years,
            "Long-Term Debt": [10000.0] * num_years,
            "Other Non-Current Liabilities": [2000.0] * num_years,
            "Retained Earnings": [8000.0] * num_years,
            "Other Equity": [5000.0] * num_years
        })

    bs_df = st.data_editor(
        st.session_state["balance_sheet_inputs"].set_index("Year"),
        num_rows="dynamic",
        use_container_width=True,
        key="bs_editor"
    )

    st.session_state["balance_sheet_inputs"].update(bs_df.reset_index())

    # Generate calculated balance sheet totals
    def generate_historical_balance_sheet(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["Total Assets"] = (
            df["Cash"] + df["Accounts Receivable"] + df["Inventory"] + df["Other Current Assets"]
            + df["Net PPE"] + df["Net Intangibles"] + df["Other Non-Current Assets"]
        )
        df["Total Liabilities"] = (
            df["Accounts Payable"] + df["Short-Term Debt"] + df["Other Current Liabilities"]
            + df["Long-Term Debt"] + df["Other Non-Current Liabilities"]
        )
        df["Total Equity"] = df["Retained Earnings"] + df["Other Equity"]
        df["Total Liabilities + Equity"] = df["Total Liabilities"] + df["Total Equity"]
        return df

    balance_sheet = generate_historical_balance_sheet(st.session_state["balance_sheet_inputs"])
    st.dataframe(balance_sheet.set_index("Year").style.format("{:,.0f}"), use_container_width=True)


# --- Tab 2: Assumptions ---
with tabs[1]:
    st.subheader("Key Assumptions (Yearly, Scenario-Based)")

    scenarios = ["Base", "Optimistic", "Worst"]
    assumption_names = [
        # Revenue & Cost Structure
        "Revenue Growth (%)",
        "COGS (% of Revenue)",
        "Admin Expenses (% of Revenue)",
        "Sales Expenses (% of Revenue)",
        "Depreciation (% of Revenue)",
        "CapEx (% of Revenue)",
    
        # Other Income/Expenses
        "Other Income (% of Revenue)",
        "Other Expenses (% of Revenue)",

        # Cash/Interest
        "Interest Rate Earned on Cash (%)",
        "Minimum Cash Balance",

        # Working Capital (Days-Based)
        "Days Receivables",
        "Days Payables",
        "Days Inventory",

        # Tax
        "Tax Rate (%)"
    ]

    if "assumptions" not in st.session_state:
        st.session_state["assumptions"] = {}

    for name in assumption_names:
        if name not in st.session_state["assumptions"]:
            st.session_state["assumptions"][name] = {}

        with st.expander(name):
            for scenario in scenarios:
                same = st.checkbox(f"Same every year ({scenario})", value=True, key=f"same_{name}_{scenario}")
                values = []
                for year in range(1, st.session_state["years"] + 1):
                    key = f"{name}_{scenario}_{year}"
                    if year == 1 or not same:
                        val = st.number_input(f"{scenario} - Year {year}", value=10.0, step=1.0, key=key)
                    else:
                        val = values[0]
                    values.append(val)
                st.session_state["assumptions"][name][scenario] = values

# --- Tab 3: Depreciation & Amortization ---
with tabs[2]:
    st.subheader("Depreciation & Amortization Inputs")

    if "da_inputs" not in st.session_state:
        st.session_state["da_inputs"] = {
            "Fixed Assets": pd.DataFrame({
                "Category": ["Machinery", "Furniture"],
                "Historical Cost": [50000, 20000],
                "Useful Life (Years)": [5, 10]
            }),
            "Intangibles": pd.DataFrame({
                "Category": ["Software"],
                "Historical Cost": [10000],
                "Useful Life (Years)": [5]
            }),
            "CapEx Forecast": pd.DataFrame({
                "Year": [datetime.now().year + i for i in range(st.session_state["years"])],
                "CapEx": [10000 for _ in range(st.session_state["years"])]
            })
        }

    st.markdown("### Fixed Assets")
    st.session_state["da_inputs"]["Fixed Assets"] = st.data_editor(
        st.session_state["da_inputs"]["Fixed Assets"], num_rows="dynamic"
    )

    st.markdown("### Intangibles")
    st.session_state["da_inputs"]["Intangibles"] = st.data_editor(
        st.session_state["da_inputs"]["Intangibles"], num_rows="dynamic"
    )

    st.markdown("### CapEx Forecast")
    st.session_state["da_inputs"]["CapEx Forecast"] = st.data_editor(
        st.session_state["da_inputs"]["CapEx Forecast"], num_rows="dynamic"
    )

# --- Tab 4: Debt ---
with tabs[3]:
    st.subheader("Debt Structure")

    if "debt_inputs" not in st.session_state:
        current_year = datetime.now().year
        st.session_state["debt_inputs"] = {
            "Existing Debt": pd.DataFrame({
                "Type": ["Short-Term", "Long-Term"],
                "Beginning Balance": [10000, 50000],
                "Interest Rate (%)": [5.0, 6.0],
                "Term (Years)": [1, 5]
            }),
            "New Debt Assumptions": pd.DataFrame({
                "Year": [current_year + i for i in range(st.session_state["years"])],
                "Amount": [0 for _ in range(st.session_state["years"])],
                "Interest Rate (%)": [7.0 for _ in range(st.session_state["years"])],
                "Term (Years)": [3 for _ in range(st.session_state["years"])]
            })
        }

    st.markdown("### Existing Debt")
    st.session_state["debt_inputs"]["Existing Debt"] = st.data_editor(
        st.session_state["debt_inputs"]["Existing Debt"], num_rows="dynamic"
    )

    st.markdown("### New Debt Assumptions")
    st.session_state["debt_inputs"]["New Debt Assumptions"] = st.data_editor(
        st.session_state["debt_inputs"]["New Debt Assumptions"], num_rows="dynamic"
    )

# Other tabs (Projections, Charts, Valuation) stay the same for now

# Place this above or near your projections tab logic
def generate_income_statement(revenue, assumptions, d_and_a, interest_paid, interest_earned, other_income, other_expense, scenario):
    ...
# --- Tab 5: Projections ---
with tabs[4]:
    st.subheader("Projections")

    scenarios = ["Base", "Optimistic", "Worst"]
    projection_results = {}

    def calculate_revenue(base_revenue, growth_rates):
        revenue = [base_revenue]
        for rate in growth_rates[1:]:
            revenue.append(revenue[-1] * (1 + rate / 100))
        return revenue

    def calculate_working_capital(revenue, cogs, assumptions, scenario):
        days_receivables = assumptions["Days Receivables"][scenario]
        days_payables = assumptions["Days Payables"][scenario]
        days_inventory = assumptions["Days Inventory"][scenario]

        receivables = []
        payables = []
        inventory = []
        net_working_capital = []

        for i in range(len(revenue)):
            annual_revenue = revenue[i]
            annual_cogs = cogs[i]

            receivable = annual_revenue * days_receivables[i] / 365
            payable = annual_cogs * days_payables[i] / 365
            inv = annual_cogs * days_inventory[i] / 365

            nwc = receivable + inv - payable

            receivables.append(receivable)
            payables.append(payable)
            inventory.append(inv)
            net_working_capital.append(nwc)

        return receivables, payables, inventory, net_working_capital

    def calculate_interest_paid(existing_debt, new_debt, years):
        interest_paid = [0.0 for _ in range(years)]
        for _, row in existing_debt.iterrows():
            balance = row["Beginning Balance"]
            rate = row["Interest Rate (%)"] / 100
            term = int(row["Term (Years)"])
            for i in range(min(term, years)):
                interest_paid[i] += balance * rate
        for i, row in new_debt.iterrows():
            year_index = i
            amount = row["Amount"]
            rate = row["Interest Rate (%)"] / 100
            term = int(row["Term (Years)"])
            for j in range(term):
                if year_index + j < years:
                    interest_paid[year_index + j] += amount * rate
        return interest_paid

    def calculate_interest_earned_from_fcf(fcf, assumptions, scenario):
        interest_earned = []
        cash_balance = []
        interest_rate = assumptions["Interest Rate Earned on Cash (%)"][scenario]
        min_cash = assumptions["Minimum Cash Balance"][scenario]  # This should be a list

        cumulative_cash = 0.0

        for i in range(len(fcf)):
            cumulative_cash += fcf[i]

            # Enforce minimum cash balance
            cash_for_interest = max(cumulative_cash, min_cash[i])

            earned = cash_for_interest * interest_rate[i] / 100

            interest_earned.append(earned)
            cash_balance.append(cash_for_interest)

        return interest_earned, cash_balance

    def generate_income_statement(revenue, assumptions, scenario):
        years = len(revenue)

        def get_assumption(key, default=0.0):
            if key in assumptions and isinstance(assumptions[key], dict):
                return assumptions[key].get(scenario, [default] * years)
            return [default] * years

        # Retrieve assumptions safely
        cogs_pct = get_assumption("COGS (% of Revenue)")
        admin_pct = get_assumption("Admin Expenses (% of Revenue)")
        sales_pct = get_assumption("Sales Expenses (% of Revenue)")
        other_inc_pct = get_assumption("Other Income (% of Revenue)")
        other_exp_pct = get_assumption("Other Expenses (% of Revenue)")
        depreciation_pct = get_assumption("Depreciation (% of Revenue)")
        amortization = [0 for _ in revenue]  # Placeholder
        tax_rate = get_assumption("Tax Rate (%)", default=25.0)  # Reasonable default
        capex_df = st.session_state["da_inputs"]["CapEx Forecast"]
        capex = capex_df["CapEx"].tolist()

        # Calculate operating components
        cogs = [r * cogs_pct[i] / 100 for i, r in enumerate(revenue)]
        admin_exp = [r * admin_pct[i] / 100 for i, r in enumerate(revenue)]
        sales_exp = [r * sales_pct[i] / 100 for i, r in enumerate(revenue)]
        other_inc = [r * other_inc_pct[i] / 100 for i, r in enumerate(revenue)]
        other_exp = [r * other_exp_pct[i] / 100 for i, r in enumerate(revenue)]
        depreciation = [r * depreciation_pct[i] / 100 for i, r in enumerate(revenue)]
    
        ebitda = [revenue[i] - cogs[i] - admin_exp[i] - sales_exp[i] for i in range(years)]
        ebit = [ebitda[i] - depreciation[i] - amortization[i] for i in range(years)]

        # Debt info from session state
        existing_debt = st.session_state["debt_inputs"]["Existing Debt"]
        new_debt = st.session_state["debt_inputs"]["New Debt Assumptions"]

        # Interest paid & earned (placeholder FCF first)
        interest_paid = calculate_interest_paid(existing_debt, new_debt, years)
        fcf_placeholder = [0.0 for _ in revenue]
        interest_earned, cash_balance = calculate_interest_earned_from_fcf(fcf_placeholder, assumptions, scenario)

        # First pass income calculation
        ebt_pre_workers = [ebit[i] - interest_paid[i] + interest_earned[i] + other_inc[i] - other_exp[i] for i in range(years)]
        workers_participation = [0.15 * e for e in ebt_pre_workers]
        taxable_income = [ebt_pre_workers[i] - workers_participation[i] for i in range(years)]
        taxes = [taxable_income[i] * tax_rate[i] / 100 for i in range(years)]
        net_income = [taxable_income[i] - taxes[i] for i in range(years)]

        # Working Capital placeholders (define your own logic above this function)
        # --- Working Capital Calculations ---
        days_receivables = assumptions["Days Receivables"][scenario]
        days_inventory = assumptions["Days Inventory"][scenario]
        days_payables = assumptions["Days Payables"][scenario]

        accounts_receivable = [revenue[i] * days_receivables[i] / 365 for i in range(len(revenue))]
        inventory = [cogs[i] * days_inventory[i] / 365 for i in range(len(revenue))]
        accounts_payable = [cogs[i] * days_payables[i] / 365 for i in range(len(revenue))]

        # Assuming no other current assets/liabilities for now
        other_current_assets = [0 for _ in revenue]
        other_current_liabilities = [0 for _ in revenue]

        net_working_capital = [
            accounts_receivable[i] + inventory[i] + other_current_assets[i]
            - accounts_payable[i] - other_current_liabilities[i]
            for i in range(len(revenue))
        ]
        delta_nwc = [net_working_capital[i] - net_working_capital[i - 1] if i > 0 else net_working_capital[0]
                     for i in range(years)]

        # FCF First Pass
        fcf = [
            ebit[i] - taxes[i] + depreciation[i] - capex[i] - delta_nwc[i]
            for i in range(years)
        ]

        debt_data = {
            scenario: {
                "years": [datetime.now().year + i for i in range(years)],
                "new_debt": new_debt["Amount"],
                "debt_repayment": new_debt["Repayment"],
                "interest_paid": interest_paid
            }
        }

        # Generate cash flow statement & chart
        cash_flow_df = generate_cash_flow_statement(
            net_income=net_income,
            depreciation=depreciation,
            capex=capex,
            delta_nwc=delta_nwc,
            debt_data=debt_data,
            scenario=scenario,
            initial_cash=historical_data["cash"][-1] if len(historical_data["cash"]) > 0 else 0.0,
        )

        st.subheader("Cash Flow Statement")
        st.dataframe(cash_flow_df.style.format("{:,.2f}"))
        st.line_chart(cash_flow_df.set_index("Year")["Ending Cash Balance"])

        # FCF table and chart
        fcf_df = pd.DataFrame({
            "Year": assumptions[scenario]["years"],
            "Free Cash Flow": fcf
        })
        st.subheader("Free Cash Flow (FCF)")
        st.dataframe(fcf_df.style.format({"Free Cash Flow": "{:,.2f}"}))
        st.line_chart(fcf_df.set_index("Year"))

        # Recalculate with real FCF-based interest earned
        interest_earned, cash_balance = calculate_interest_earned_from_fcf(fcf, assumptions, scenario)
        ebt_pre_workers = [ebit[i] - interest_paid[i] + interest_earned[i] + other_inc[i] - other_exp[i] for i in range(years)]
        workers_participation = [0.15 * e for e in ebt_pre_workers]
        taxable_income = [ebt_pre_workers[i] - workers_participation[i] for i in range(years)]
        taxes = [taxable_income[i] * tax_rate[i] / 100 for i in range(years)]
        net_income = [taxable_income[i] - taxes[i] for i in range(years)]
        fcf = [ebit[i] - taxes[i] + depreciation[i] - capex[i] - delta_nwc[i] for i in range(years)]


        # Re-render charts with final FCF
        cash_flow_df = generate_cash_flow_statement(
            net_income=net_income,
            depreciation=depreciation,
            capex=capex,
            delta_nwc=delta_nwc,
            debt_data=debt_data,
            scenario=scenario,
            historical_data = st.session_state.get("historical_data", {})
            initial_cash = historical_data.get("Efectivo y Equivalentes", [0.0])[-1] if "Efectivo y Equivalentes" in historical_data else 0.0
        )

        st.subheader("Cash Flow Statement")
        st.dataframe(cash_flow_df.style.format("{:,.2f}"))
        st.line_chart(cash_flow_df.set_index("Year")["Ending Cash Balance"])

        fcf_df = pd.DataFrame({
            "Year": assumptions[scenario]["years"],
            "Free Cash Flow": fcf
        })
        st.subheader("Free Cash Flow (FCF)")
        st.dataframe(fcf_df.style.format({"Free Cash Flow": "{:,.2f}"}))
        st.line_chart(fcf_df.set_index("Year"))

        # Final output dataframe
        return pd.DataFrame({
            "Year": [datetime.now().year + i for i in range(years)],
            "Revenue": revenue,
            "COGS": cogs,
            "Admin Expenses": admin_exp,
            "Sales Expenses": sales_exp,
            "EBITDA": ebitda,
            "Depreciation": depreciation,
            "Amortization": amortization,
            "EBIT": ebit,
            "Interest Paid": interest_paid,
            "Interest Earned": interest_earned,
            "Cash Balance": cash_balance,
            "Other Income": other_inc,
            "Other Expenses": other_exp,
            "EBT (Pre Workers)": ebt_pre_workers,
            "Workers Participation": workers_participation,
            "Taxable Income": taxable_income,
            "Taxes": taxes,
            "Net Income": net_income,
            "Free Cash Flow": fcf
        })
    base_revenue = st.session_state["historical_data"]["Ingresos"].iloc[-1]

    for scenario in scenarios:
        st.markdown(f"### Scenario: {scenario}")
        growth = st.session_state["assumptions"]["Revenue Growth (%)"][scenario]
        revenue = calculate_revenue(base_revenue, growth)
        df_proj = generate_income_statement(revenue, st.session_state["assumptions"], scenario)
        projection_results[scenario] = df_proj
        st.dataframe(df_proj)

    def generate_cash_flow_statement(
        net_income: list,
        depreciation: list,
        capex: list,
        delta_nwc: list,
        debt_data: dict,
        scenario: str,
        initial_cash: float = 0.0
    ) -> pd.DataFrame:
        years = debt_data[scenario]["years"]
        new_debt = debt_data[scenario]["new_debt"]
        debt_repayment = debt_data[scenario]["debt_repayment"]
        interest_paid = debt_data[scenario]["interest_paid"]

        cash_from_ops = [
            net_income[i] + depreciation[i] - delta_nwc[i]
            for i in range(len(years))
        ]
    
        cash_from_investing = [-capex[i] for i in range(len(years))]
    
        cash_from_financing = [
            new_debt[i] - debt_repayment[i] - interest_paid[i]
            for i in range(len(years))
        ]
    
        net_cash_flow = [
            cash_from_ops[i] + cash_from_investing[i] + cash_from_financing[i]
            for i in range(len(years))
        ]

        ending_cash = []
        for i in range(len(years)):
            if i == 0:
                ending_cash.append(initial_cash + net_cash_flow[i])
            else:
                ending_cash.append(ending_cash[i - 1] + net_cash_flow[i])

        return pd.DataFrame({
            "Year": years,
            "Cash from Operating": cash_from_ops,
            "Cash from Investing": cash_from_investing,
            "Cash from Financing": cash_from_financing,
            "Net Cash Flow": net_cash_flow,
            "Ending Cash Balance": ending_cash,
        }) 

    def generate_balance_sheet(
        years: list,
        revenue: list,
        ending_cash: list,
        net_ppe: list,
        net_intangibles: list,
        delta_receivables: list,
        delta_inventory: list,
        delta_payables: list,
        debt_data: dict,
        net_income: list,
        scenario: str,
        other_current_assets: list,
        other_non_current_assets: list,
        other_current_liabilities: list,
        other_non_current_liabilities: list,
        other_equity: list,
        initial_retained_earnings: float = 0.0,
    ) -> pd.DataFrame:

        # Working Capital Items
        accounts_receivable = [delta_receivables[0]]
        inventory = [delta_inventory[0]]
        accounts_payable = [delta_payables[0]]
    
        for i in range(1, len(years)):
            accounts_receivable.append(accounts_receivable[i-1] + delta_receivables[i])
            inventory.append(inventory[i-1] + delta_inventory[i])
            accounts_payable.append(accounts_payable[i-1] + delta_payables[i])

        # Retained Earnings
        retained_earnings = []
        for i in range(len(years)):
            if i == 0:
                retained_earnings.append(initial_retained_earnings + net_income[i])
            else:
                retained_earnings.append(retained_earnings[i-1] + net_income[i])

        # Debt
        short_term_debt = debt_data[scenario]["short_term_debt"]
        long_term_debt = debt_data[scenario]["long_term_debt"]

        # Total Assets
        total_assets = [
            ending_cash[i]
            + accounts_receivable[i]
            + inventory[i]
            + net_ppe[i]
            + net_intangibles[i]
            + other_current_assets[i]
            + other_non_current_assets[i]
            for i in range(len(years))
        ]

        # Total Liabilities
        total_liabilities = [
            accounts_payable[i]
            + short_term_debt[i]
            + long_term_debt[i]
            + other_current_liabilities[i]
            + other_non_current_liabilities[i]
            for i in range(len(years))
        ]

        # Total Equity
        total_equity = [
            retained_earnings[i] + other_equity[i]
            for i in range(len(years))
        ]

        return pd.DataFrame({
            "Year": years,
            # Assets
            "Cash": ending_cash,
            "Accounts Receivable": accounts_receivable,
            "Inventory": inventory,
            "Other Current Assets": other_current_assets,
            "Net PPE": net_ppe,
            "Net Intangibles": net_intangibles,
            "Other Non-Current Assets": other_non_current_assets,
            "Total Assets": total_assets,

            # Liabilities
            "Accounts Payable": accounts_payable,
            "Short-Term Debt": short_term_debt,
            "Other Current Liabilities": other_current_liabilities,
            "Long-Term Debt": long_term_debt,
            "Other Non-Current Liabilities": other_non_current_liabilities,
            "Total Liabilities": total_liabilities,

            # Equity
            "Retained Earnings": retained_earnings,
            "Other Equity": other_equity,
            "Total Equity": total_equity,

            # Control Total
            "Total Liabilities + Equity": [
                total_liabilities[i] + total_equity[i] for i in range(len(years))
            ]
        })
  
# --- Tab 6: Charts ---
with tabs[5]:
    st.subheader("Charts")
    metric = st.selectbox("Select Metric", ["Revenue", "EBIT", "Net Income", "FCF"])
    chart_df = pd.DataFrame({
        scenario: projection_data[scenario][metric] for scenario in scenarios
    })
    chart_df.index = projection_data[scenarios[0]]["Year"]
    st.line_chart(chart_df)

# --- Tab 7: Valuation ---
with tabs[6]:
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