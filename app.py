
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
    
    new_debt = st.data_editor(
        st.session_state["debt_inputs"]["New Debt Assumptions"],
        num_rows="dynamic"
    )

    new_debt["Repayment"] = new_debt.apply(
        lambda row: row["Amount"] / row["Term (Years)"] if row["Term (Years)"] else 0,
        axis=1
    )

    st.session_state["debt_inputs"]["New Debt Assumptions"] = new_debt

    st.markdown("### Existing Debt")
    st.session_state["debt_inputs"]["Existing Debt"] = st.data_editor(
        st.session_state["debt_inputs"]["Existing Debt"], num_rows="dynamic"
    )

    st.markdown("### New Debt Assumptions")
    

# Other tabs (Projections, Charts, Valuation) stay the same for now

# Place this above or near your projections tab logic
def generate_income_statement(revenue, assumptions, d_and_a, interest_paid, interest_earned, other_income, other_expense, scenario):
    ...
# --- Tab 5: Projections ---
with tabs[4]:
    st.header("Projections")

    # Selección de escenario
    scenario = st.selectbox("Select scenario", ["Base", "Optimistic", "Worst"])
    assumptions = {}
    for name in st.session_state["assumptions"]:
        assumptions[name] = st.session_state["assumptions"][name][scenario]

    # Subtabs: Income Statement, Cash Flow, Balance Sheet
    subtab_labels = ["Estado de Resultados", "Flujo de Caja", "Balance General"]
    subtab_objs = st.tabs(subtab_labels)

    # Inicialización de estructuras de datos
    income_statement = []
    cash_flow = []
    balance_sheet = []

    historical_data = st.session_state.get("historical_data", pd.DataFrame())

    historical_years = historical_data["Year"].tolist()
    start_year = max(historical_years)
    projection_years = list(range(start_year + 1, start_year + assumptions["Years"] + 1))

    # Valores iniciales desde el último año histórico
    last_row = historical_data[historical_data["Year"] == start_year].iloc[0]
    prev_cash = last_row["Cash"]
    prev_assets = last_row["Total Assets"]
    prev_equity = last_row["Equity"]
    prev_debt = last_row["Short-term Debt"] + last_row["Long-term Debt"]

    def calculate_debt_schedule(debt_inputs, projection_years):
        existing_df = debt_inputs["Existing Debt"]
        new_df = debt_inputs["New Debt Assumptions"]

        short_row = existing_df[existing_df["Type"] == "Short-Term"].iloc[0]
        long_row = existing_df[existing_df["Type"] == "Long-Term"].iloc[0]

        current_short = short_row["Beginning Balance"]
        current_long = long_row["Beginning Balance"]
        rate_short = short_row["Interest Rate (%)"] / 100
        rate_long = long_row["Interest Rate (%)"] / 100
        term_short = short_row["Term (Years)"]
        term_long = long_row["Term (Years)"]

        debt_schedule = {
            "short_term": {},
            "long_term": {},
            "interest_expense": {}
        }

        for year in projection_years:
            # Interest on existing debt
            interest = current_short * rate_short + current_long * rate_long

            # Add new debt this year (if any)
            row = new_df[new_df["Year"] == year]
            if not row.empty:
                new_amt = row["Amount"].values[0]
                new_rate = row["Interest Rate (%)"].values[0] / 100
                #new_term = row["Term (Years)"].values[0]
                interest += new_amt * new_rate

                # Add new debt to long-term (could customize logic here)
                current_long += new_amt

            # Save schedule
            debt_schedule["short_term"][year] = current_short
            debt_schedule["long_term"][year] = current_long
            debt_schedule["interest_expense"][year] = interest

            # Amortize principal (equal installments)
            current_short = max(0, current_short - (short_row["Beginning Balance"] / term_short if term_short > 0 else 0))
            current_long = max(0, current_long - (long_row["Beginning Balance"] / term_long if term_long > 0 else 0))

        return debt_schedule

    def calculate_da_schedule(da_inputs, projection_years):
            da_by_year = {year: 0 for year in projection_years}

            # Fixed Assets (historical)
            for _, row in da_inputs["Fixed Assets"].iterrows():
                cost = row["Historical Cost"]
                life = int(row["Useful Life (Years)"])
                annual_dep = cost / life
                for i in range(min(life, len(projection_years))):
                    year = projection_years[i]
                    da_by_year[year] += annual_dep

            # Intangibles (historical)
            for _, row in da_inputs["Intangibles"].iterrows():
                cost = row["Historical Cost"]
                life = int(row["Useful Life (Years)"])
                annual_amort = cost / life
                for i in range(min(life, len(projection_years))):
                    year = projection_years[i]
                    da_by_year[year] += annual_amort

            # CapEx Forecast
            for _, row in da_inputs["CapEx Forecast"].iterrows():
                year = int(row["Year"])
                capex = row["CapEx"]
                life = 5  # You can customize this or make it user input later
                for offset in range(life):
                    y = year + offset
                    if y in da_by_year:
                       da_by_year[y] += capex / life

            return da_by_year

    debt_inputs = st.session_state["debt_inputs"]
    da_inputs = st.session_state["da_inputs"]
    debt_data = calculate_debt_schedule(debt_inputs, projection_years)
    d_and_a_data = calculate_da_schedule(da_inputs, projection_years)

    projected_income_statements = {}
    projected_cash_flows = {}

    for year in projection_years:
        # --- Estado de Resultados ---
        revenue = assumptions["Revenue"][0] * (1 + assumptions["Revenue Growth"]/100) ** (year - projection_years[0])
        cogs = revenue * assumptions["COGS %"] / 100
        admin_expenses = revenue * assumptions["Admin Expenses %"] / 100
        sales_expenses = revenue * assumptions["Sales Expenses %"] / 100
        other_income = revenue * assumptions["Other Income %"] / 100
        

        # Depreciación y Amortización
        d_a = d_and_a_data.get(year, 0)

        # EBIT
        ebit = revenue - cogs - admin_expenses - sales_expenses + other_income - d_a

        # Intereses
        interest_expense = debt_data.get('interest_expense', {}).get(year, 0)
        interest_income = prev_cash * assumptions["Interest Rate on Cash"] / 100

        ebt = ebit - interest_expense + interest_income

        # Impuesto (ajustado por participación de trabajadores)
        workers_participation = 0.15 * ebt if ebt > 0 else 0
        taxable_income = ebt - workers_participation
        taxes = taxable_income * assumptions["Tax Rate"] / 100 if taxable_income > 0 else 0

        net_income = ebt - taxes

        income_statement.append({
            "Year": year,
            "Revenue": revenue,
            "COGS": cogs,
            "Admin Expenses": admin_expenses,
            "Sales Expenses": sales_expenses,
            "Other Income": other_income,
            "D&A": d_a,
            "EBIT": ebit,
            "Interest Expense": interest_expense,
            "Interest Income": interest_income,
            "EBT": ebt,
            "Taxes": taxes,
            "Net Income": net_income
        })

        # --- Flujo de Caja ---
        capex = d_and_a_data.get('capex', {}).get(year, 0)
        change_in_wcap = 0  # Simplificado por ahora

        operating_cf = net_income + d_a - change_in_wcap
        investing_cf = -capex
        financing_cf = -debt_data.get("principal_payment", {}).get(year, 0) + debt_data.get("new_debt", {}).get(year, 0)

        net_cash_flow = operating_cf + investing_cf + financing_cf
        ending_cash = prev_cash + net_cash_flow

        cash_flow.append({
            "Year": year,
            "Operating CF": operating_cf,
            "Investing CF": investing_cf,
            "Financing CF": financing_cf,
            "Net Cash Flow": net_cash_flow,
            "Ending Cash": ending_cash
        })

        # --- Balance General ---
        total_assets = prev_assets + net_cash_flow  # muy simplificado
        total_liabilities = debt_data.get("ending_balance", {}).get(year, prev_debt)
        equity = total_assets - total_liabilities

        balance_sheet.append({
            "Year": year,
            "Cash": ending_cash,
            "Total Assets": total_assets,
            "Debt": total_liabilities,
            "Equity": equity
        })

        # Actualizar para el siguiente año
        prev_cash = ending_cash
        prev_assets = total_assets
        prev_debt = total_liabilities
        prev_equity = equity

    # Guardar resultados por escenario
    income_df = pd.DataFrame(income_statement)
    cash_df = pd.DataFrame(cash_flow)
    projected_income_statements[scenario] = income_df
    projected_cash_flows[scenario] = cash_df

    # Construir projection_data para Charts
    projection_data = {}
    for scen in projected_income_statements:
        inc = projected_income_statements[scen]
        cf = projected_cash_flows[scen]
        projection_data[scen] = {
            "Year": inc["Year"],
            "Revenue": inc["Revenue"],
            "EBIT": inc["EBIT"],
            "Net Income": inc["Net Income"],
            "FCF": cf["Net Cash Flow"]
        }

    st.session_state["projection_data"] = projection_data

    # Mostrar en subtabs
    with subtab_objs[0]:
        st.subheader("Estado de Resultados")
        st.dataframe(pd.DataFrame(income_statement))

    with subtab_objs[1]:
        st.subheader("Flujo de Caja")
        st.dataframe(pd.DataFrame(cash_flow))

    with subtab_objs[2]:
        st.subheader("Balance General")
        st.dataframe(pd.DataFrame(balance_sheet))
  
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