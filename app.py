
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
    projection_years = list(range(start_year + 1, start_year + st.session_state["years"] + 1))


    # Valores iniciales desde el último año histórico
    # Don't overwrite the list `balance_sheet`
    historical_bs_df = generate_historical_balance_sheet(st.session_state["balance_sheet_inputs"])

    # Get the starting values from the latest historical year
    bs_row = historical_bs_df[historical_bs_df["Year"] == start_year]
    if bs_row.empty:
        st.error(f"No balance sheet data found for year {start_year}")
        st.stop()

    bs_row = bs_row.iloc[0]

    prev_ppe = float(bs_row["Net PPE"])
    other_assets_static = float(prev_assets - prev_cash - prev_ppe)
    prev_total_liabilities = float(bs_row["Total Liabilities"])
    other_liabilities_static = float(prev_total_liabilities - prev_debt)

    prev_revenue = float(historical_data.loc[historical_data["Year"] == start_year, "Ingresos"].iloc[0])
    prev_cogs = float(historical_data.loc[historical_data["Year"] == start_year, "Costo de Ventas"].iloc[0])
    prev_ar = prev_revenue * assumptions["Days Receivables"][0] / 365.0
    prev_inv = prev_cogs * assumptions["Days Inventory"][0] / 365.0
    prev_ap = prev_cogs * assumptions["Days Payables"][0] / 365.0

    prev_cash = bs_row["Cash"]
    prev_assets = bs_row["Total Assets"]
    prev_equity = bs_row["Total Equity"]
    prev_debt = bs_row["Short-Term Debt"] + bs_row["Long-Term Debt"]


    def calculate_debt_schedule(debt_inputs, projection_years):
        existing_df = debt_inputs["Existing Debt"].copy()
        new_df = debt_inputs["New Debt Assumptions"].copy()

        short = existing_df[existing_df["Type"] == "Short-Term"].iloc[0]
        long = existing_df[existing_df["Type"] == "Long-Term"].iloc[0]

        current_short = float(short["Beginning Balance"])
        current_long = float(long["Beginning Balance"])
        rate_short = float(short["Interest Rate (%)"]) / 100.0
        rate_long = float(long["Interest Rate (%)"]) / 100.0
        remaining_short_years = int(short["Term (Years)"]) or 0
        remaining_long_years = int(long["Term (Years)"]) or 0
        base_short_principal = (current_short / remaining_short_years) if remaining_short_years > 0 else 0.0
        base_long_principal = (current_long / remaining_long_years) if remaining_long_years > 0 else 0.0

        # Track principal for new issuances by year
        new_long_principal_by_year = {}

        schedule = {
            "short_term": {},
            "long_term": {},
            "interest_expense": {},
            "principal_payment": {},
            "new_debt": {},
            "ending_balance": {}
        }

        for year in projection_years:
            beginning_short = current_short
            beginning_long = current_long

            # New debt this year (added to long-term)
            row = new_df[new_df["Year"] == year]
            new_amount = float(row["Amount"].values[0]) if not row.empty else 0.0
            new_rate = float(row["Interest Rate (%)"].values[0]) / 100.0 if not row.empty else 0.0
            new_term = int(row["Term (Years)"].values[0]) if not row.empty else 0

            if new_amount > 0:
                current_long += new_amount
                if new_term > 0:
                    annual_p = new_amount / new_term
                    for i in range(1, new_term + 1):
                        new_long_principal_by_year[year + i] = new_long_principal_by_year.get(year + i, 0.0) + annual_p

            # Interest (simple approximation)
            interest = beginning_short * rate_short + beginning_long * rate_long + new_amount * new_rate

            # Principal due this year
            pay_short = base_short_principal if remaining_short_years > 0 else 0.0
            pay_long_base = base_long_principal if remaining_long_years > 0 else 0.0
            pay_long_new = new_long_principal_by_year.get(year, 0.0)

            total_principal = min(pay_short, current_short) + min(pay_long_base + pay_long_new, current_long)

            # Apply payments
            current_short = max(0.0, current_short - pay_short)
            current_long = max(0.0, current_long - (pay_long_base + pay_long_new))

            remaining_short_years = max(0, remaining_short_years - 1)
            remaining_long_years = max(0, remaining_long_years - 1)

            schedule["short_term"][year] = current_short
            schedule["long_term"][year] = current_long
            schedule["interest_expense"][year] = interest
            schedule["principal_payment"][year] = total_principal
            schedule["new_debt"][year] = new_amount
            schedule["ending_balance"][year] = current_short + current_long

        return schedule

    def calculate_da_schedule(da_inputs, projection_years):
        da_by_year = {year: 0.0 for year in projection_years}
        capex_by_year = {year: 0.0 for year in projection_years}

        # Fixed Assets (historical)
        for _, row in da_inputs["Fixed Assets"].iterrows():
            cost = float(row["Historical Cost"])
            life = int(row["Useful Life (Years)"]) or 1
            annual = cost / life
            for y in projection_years[:life]:
                da_by_year[y] += annual

        # Intangibles (historical)
        for _, row in da_inputs["Intangibles"].iterrows():
            cost = float(row["Historical Cost"])
            life = int(row["Useful Life (Years)"]) or 1
            annual = cost / life
            for y in projection_years[:life]:
                da_by_year[y] += annual

        # CapEx Forecast and resulting depreciation (straight-line over 10 years)
        default_life = 10
        for _, row in da_inputs["CapEx Forecast"].iterrows():
            year = int(row["Year"])
            capex = float(row["CapEx"])
            if year in capex_by_year:
                capex_by_year[year] += capex
            annual = capex / default_life
            for i in range(default_life):
                y = year + i
                if y in da_by_year:
                    da_by_year[y] += annual

        return {"da": da_by_year, "capex": capex_by_year}

    debt_inputs = st.session_state["debt_inputs"]
    da_inputs = st.session_state["da_inputs"]
    debt_data = calculate_debt_schedule(debt_inputs, projection_years)
    d_and_a_data = calculate_da_schedule(da_inputs, projection_years)

    projected_income_statements = {}
    projected_cash_flows = {}

    for year in projection_years:
        # --- Estado de Resultados ---
        year_index = year - projection_years[0]
        growth_rate = assumptions["Revenue Growth (%)"][year_index] / 100.0
        revenue = prev_revenue * (1.0 + growth_rate)
        cogs_pct = assumptions["COGS (% of Revenue)"][year_index]
        cogs = revenue * cogs_pct / 100.0
        admin_exp_pct = assumptions["Admin Expenses (% of Revenue)"][year_index]
        admin_expenses = revenue * admin_exp_pct / 100
        sale_exp_pct = assumptions["Sales Expenses (% of Revenue)"][year_index]
        sales_expenses = revenue * sale_exp_pct / 100
        other_inc_pct =  assumptions["Other Income (% of Revenue)"][year_index]
        other_income = revenue * other_inc_pct/ 100
        

        # Depreciación y Amortización
        d_a = d_and_a_data["da"].get(year, 0.0)
        capex = d_and_a_data["capex"].get(year, 0.0)

        # EBIT
        ebit = revenue - cogs - admin_expenses - sales_expenses + other_income - d_a

        # Intereses
        interest_expense = debt_data.get("interest_expense", {}).get(year, 0.0)
        interest_rate = assumptions["Interest Rate Earned on Cash (%)"][year_index]
        interest_income = prev_cash * interest_rate / 100.0

        days_rec = assumptions["Days Receivables"][year_index]
        days_inv = assumptions["Days Inventory"][year_index]
        days_pay = assumptions["Days Payables"][year_index]

        ar = revenue * days_rec / 365.0
        inv = cogs * days_inv / 365.0
        ap = cogs * days_pay / 365.0
        change_in_wcap = (ar - prev_ar) + (inv - prev_inv) - (ap - prev_ap)

        ebt = ebit - interest_expense + interest_income

        # Impuesto (ajustado por participación de trabajadores)
        workers_participation = 0.15 * ebt if ebt > 0 else 0
        taxable_income = ebt - workers_participation
        tax_rate = assumptions["Tax Rate (%)"][year_index]
        taxes = taxable_income * tax_rate / 100 if taxable_income > 0 else 0

        net_income = ebt - taxes

        income_statement.append({
            "Year": year,
            "Ingresos": revenue,
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
        principal_payment = debt_data.get("principal_payment", {}).get(year, 0.0)
        new_debt_year = debt_data.get("new_debt", {}).get(year, 0.0)
        financing_cf = -principal_payment + new_debt_year

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
        ppe = prev_ppe + capex - d_a
        total_assets = ending_cash + ppe + other_assets_static
        total_liabilities = other_liabilities_static + debt_data.get("ending_balance", {}).get(year, prev_debt)
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
        prev_debt = total_liabilities - other_liabilities_static
        prev_equity = equity
        prev_ppe = ppe
        prev_revenue = revenue
        prev_cogs = cogs
        prev_ar, prev_inv, prev_ap = ar, inv, ap


    def build_er_df(income_rows: list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(income_rows)
        cols = ["Year","Ingresos","COGS","Admin Expenses","Sales Expenses","Other Income","D&A","EBIT","Interest Expense","Interest Income","EBT","Taxes","Net Income"]
        df = df[cols].copy()

        rows = [
            ("VENTAS NETAS", "Ingresos"),
            ("(-) COSTO DE VENTAS", "COGS"),
            ("UTILIDAD BRUTA", df["Ingresos"] - df["COGS"]),
            ("(-) GASTOS DE ADMINISTRACION", "Admin Expenses"),
            ("(-) GASTOS DE VENTAS", "Sales Expenses"),
            ("UTILIDAD ANTES DE DEP Y AMORT (EBITDA)", (df["Ingresos"] - df["COGS"] - df["Admin Expenses"] - df["Sales Expenses"])),
            ("(-) DEPRECIACION Y AMORTIZACION", "D&A"),
            ("UTILIDAD OPERATIVA (EBIT)", "EBIT"),
            ("(+) OTROS INGRESOS NO OPERATIVOS", "Other Income"),
            ("UTILIDAD ANTES DE IMPUESTOS (EBT) (después de int.)", df["EBT"]),
            ("(-) IMPUESTOS", "Taxes"),
            ("UTILIDAD NETA", "Net Income")
        ]

        out = []
        years = df["Year"].tolist()
        for label, source in rows:
            if isinstance(source, str):
                series = df[source].values
            else:
                series = source.values
            out.append(pd.Series(series, name=label))
        er = pd.concat(out, axis=1).T
        er.columns = [pd.to_datetime(f"{y}-12-31") for y in years]
        return er

    def build_bg_df(balance_rows: list[dict], ar_series: dict[int,float], inv_series: dict[int,float], ap_series: dict[int,float], ppe_series: dict[int,float]) -> pd.DataFrame:
        df = pd.DataFrame(balance_rows)
        years = df["Year"].tolist()
        cash = df.set_index("Year")["Cash"]
        total_assets = df.set_index("Year")["Total Assets"]
        debt = df.set_index("Year")["Debt"]
        equity = df.set_index("Year")["Equity"]

        # Map WC and PPE from your loop
        ar = pd.Series({y: ar_series.get(y, 0.0) for y in years})
        inv = pd.Series({y: inv_series.get(y, 0.0) for y in years})
        ap = pd.Series({y: ap_series.get(y, 0.0) for y in years})
        ppe = pd.Series({y: ppe_series.get(y, 0.0) for y in years})

        rows = [
            ("ACTIVO", None),
            ("CAJA Y BANCOS", cash.values),
            ("CUENTAS POR COBRAR COMERCIALES", ar.values),
            ("(-) PROVISION CUENTAS INCOBRABLES COMERCIALES", np.zeros(len(years))),  # keep 0 unless you model it
            ("INVENTARIOS", inv.values),
            ("PROPIEDAD PLANTA Y EQUIPO, NETO", ppe.values),
            ("TOTAL ACTIVOS", total_assets.values),
            ("PASIVO Y PATRIMONIO", None),
            ("DEUDA TOTAL", debt.values),
            ("PATRIMONIO", equity.values),
            ("TOTAL PASIVO + PATRIMONIO", (debt + equity).values),
        ]

        out = []
        for label, series in rows:
            if series is None:
                s = pd.Series([np.nan] * len(years), name=label)
            else:
                s = pd.Series(series, name=label)
            out.append(s)
        bg = pd.concat(out, axis=1).T
        bg.columns = [pd.to_datetime(f"{y}-12-31") for y in years]
        return bg

    def build_flujo_df(income_rows: list[dict], cash_rows: list[dict], wc_changes: dict[int,dict[str,float]], capex_by_year: dict[int,float], debt_sched: dict) -> pd.DataFrame:
        inc = pd.DataFrame(income_rows).set_index("Year")
        cash = pd.DataFrame(cash_rows).set_index("Year")
        years = inc.index.tolist()

        d_a = inc["D&A"]
        net_income = inc["Net Income"]

        # WC deltas from your loop (provide dict per year with keys: delta_ar, delta_inv, delta_ap)
        delta_ar = pd.Series({y: wc_changes.get(y, {}).get("delta_ar", 0.0) for y in years})
        delta_inv = pd.Series({y: wc_changes.get(y, {}).get("delta_inv", 0.0) for y in years})
        delta_ap = pd.Series({y: wc_changes.get(y, {}).get("delta_ap", 0.0) for y in years})
        change_in_wcap = delta_ar + delta_inv - delta_ap

        capex = pd.Series({y: capex_by_year.get(y, 0.0) for y in years})
        principal = pd.Series({y: debt_sched.get("principal_payment", {}).get(y, 0.0) for y in years})
        new_debt = pd.Series({y: debt_sched.get("new_debt", {}).get(y, 0.0) for y in years})

        operating_cf = net_income + d_a - change_in_wcap
        investing_cf = -capex
        financing_cf = -principal + new_debt
        net_cf = operating_cf + investing_cf + financing_cf

        rows = [
            ("FLUJO DE EFECTIVO GENERADO POR  ACT. DE OPERACIÓN", None),
            ("Utilidad Neta", net_income.values),
            ("(+) Depreciacion, Amortizacion Y Provisiones", d_a.values),
            ("Cambio Ctas por Cobrar Comerciales", delta_ar.values),
            ("Cambio Inventarios", delta_inv.values),
            ("Cambio Ctas por Pagar Comerciales", delta_ap.values),
            ("Flujo Operación", operating_cf.values),
            ("FLUJO DE EFECTIVO DE ACTIVIDADES DE INVERSION", None),
            ("(-) Compra de Activos Fijos (CapEx)", (-capex).values),
            ("Flujo Inversión", investing_cf.values),
            ("FLUJO DE EFECTIVO DE ACTIVIDADES DE FINANCIAMIENTO", None),
            ("(-) Amortización de Deuda", (-principal).values),
            ("(+) Nueva Deuda", new_debt.values),
            ("Flujo Financiamiento", financing_cf.values),
            ("AUMENTO (DISMINUCIÓN) NETO DE EFECTIVO", net_cf.values),
            ("EFECTIVO FINAL", cash["Ending Cash"].reindex(years).values),
        ]

        out = []
        for label, series in rows:
            s = pd.Series([np.nan]*len(years), name=label) if series is None else pd.Series(series, name=label)
            out.append(s)
        flujo = pd.concat(out, axis=1).T
        flujo.columns = [pd.to_datetime(f"{y}-12-31") for y in years]
        return flujo

     # Guardar resultados por escenario
    income_df = pd.DataFrame(income_statement)
    cash_df = pd.DataFrame(cash_flow)
    balance_df = pd.DataFrame(balance_sheet)

    proj_df = pd.DataFrame({
        "Year": income_df["Year"],
        "Ingresos": income_df["Ingresos"],
        "EBIT": income_df["EBIT"],
        "Net Income": income_df["Net Income"],
        "FCF": cash_df["Net Cash Flow"]
    })

    st.session_state.setdefault("projection_data", {})
    st.session_state["projection_data"][scenario] = proj_df

    # Construir projection_data para Charts
    projection_data = {}
    for scen in projected_income_statements:
        inc = projected_income_statements[scen]
        cf = projected_cash_flows[scen]
        projection_data[scen] = {
            "Year": inc["Year"],
            "Ingresos": inc["Ingresos"],
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
    metric = st.selectbox("Select Metric", ["Ingresos", "EBIT", "Net Income", "FCF"])

    available = st.session_state.get("projection_data", {})
    scen = st.selectbox("Scenario", list(available.keys()) or ["Base"])
    if scen in available:
        df_plot = available[scen]
        st.line_chart(df_plot.set_index("Year")[[metric]])
    else:
        st.warning("No projection data available. Please run the Projections tab.")

# --- Tab 7: Valuation ---
with tabs[6]:
    st.subheader("Valuation (Discounted Cash Flow)")
    discount_rate = st.number_input("Discount Rate (%)", value=10.0, step=0.5)

    available = st.session_state.get("projection_data", {})
    scen = st.selectbox("Scenario", list(available.keys()) or ["Base"], key="valuation_scenario")
    if scen in available:
        df = available[scen]
        fcf = df["FCF"].tolist()
        discounted_fcf = [fcf[i] / (1 + discount_rate / 100.0) ** (i + 1) for i in range(len(fcf))]
        valuation = float(np.nansum(discounted_fcf))
        st.metric("Valuation", f"${valuation:,.0f}")

        if st.button("Download Projections to Excel"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Projections", index=False)
            st.download_button(
                label="Download Excel File",
                data=output.getvalue(),
                file_name="financial_model.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("No projection data available. Please complete the Projections tab first.")