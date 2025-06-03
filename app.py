
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


# Define tabs
tabs = st.tabs([
    "Historical Data", "Assumptions", "Depreciation & Amortization", "Debt",
    "Projections", "Charts", "Valuation"
])

# --- Tab 1: Historical Data ---
with tabs[0]:
    st.subheader("Historical Financial Data")

    # Define input columns editable by the user (all base inputs + impuestos y participacion)
    input_cols = [
        "Ingresos", "Costo de Ventas", "Gastos Administración", "Gastos Ventas",
        "Depreciación", "Amortización", "Otros Ingresos No Operativos", "Otros Gastos No Operativos",
        "Resultado Financiero Neto", "Participación de Trabajadores", "Impuestos"
    ]

    # Initialize session_state with default columns if missing
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

    # Show editable inputs in a data editor
    df_inputs = st.data_editor(
        st.session_state["historical_data"][["Year"] + input_cols].set_index("Year"),
        num_rows="dynamic",
        use_container_width=True
    )

    # Update session state with user edits
    st.session_state["historical_data"].update(df_inputs.reset_index())

    # Extract columns for calculation
    ingresos = st.session_state["historical_data"]["Ingresos"]
    costo_ventas = st.session_state["historical_data"]["Costo de Ventas"]
    gastos_admin = st.session_state["historical_data"]["Gastos Administración"]
    gastos_ventas = st.session_state["historical_data"]["Gastos Ventas"]
    depreciacion = st.session_state["historical_data"]["Depreciación"]
    amortizacion = st.session_state["historical_data"]["Amortización"]
    otros_ingresos = st.session_state["historical_data"]["Otros Ingresos No Operativos"]
    otros_gastos = st.session_state["historical_data"]["Otros Gastos No Operativos"]
    resultado_financiero = st.session_state["historical_data"]["Resultado Financiero Neto"]
    participacion_trabajadores = st.session_state["historical_data"]["Participación de Trabajadores"]
    impuestos = st.session_state["historical_data"]["Impuestos"]

    # Calculate required metrics
    utilidad_bruta = ingresos - costo_ventas
    ebitda = utilidad_bruta - gastos_admin - gastos_ventas
    ebit = ebitda - depreciacion - amortizacion
    ebt = ebit + otros_ingresos - otros_gastos + resultado_financiero
    utilidad_neta = ebt - participacion_trabajadores - impuestos

    # Create income statement DataFrame for display (transpose for readability)
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
    }, index=st.session_state["historical_data"]["Year"]).T

    st.markdown("### Income Statement (Calculated Fields & Inputs)")
    st.dataframe(income_statement)

# --- Tab 2: Assumptions ---
with tabs[1]:
    st.subheader("Key Assumptions (Yearly, Scenario-Based)")

    scenarios = ["Base", "Optimistic", "Worst"]
    assumption_names = [
        "Revenue Growth (%)",
        "COGS (% of Revenue)",
        "Admin Expenses (% of Revenue)",
        "Sales Expenses (% of Revenue)",
        "Other Income (% of Revenue)",
        "Other Expenses (% of Revenue)",
        "Depreciation (% of Revenue)",
        "CapEx (% of Revenue)",
        "Working Capital (% of Revenue)",
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
    projection_data = {}

    assumptions = st.session_state["assumptions"]

    def generate_income_statement(revenue, assumptions, scenario):
        cogs = [r * assumptions["COGS (% of Revenue)"][scenario][i] / 100 for i, r in enumerate(revenue)]
        admin_exp = [r * assumptions.get("Admin Expenses (% of Revenue)", {"Base": [0]*len(revenue)})[scenario][i] / 100 for i, r in enumerate(revenue)]
        sales_exp = [r * assumptions.get("Sales Expenses (% of Revenue)", {"Base": [0]*len(revenue)})[scenario][i] / 100 for i, r in enumerate(revenue)]
        other_inc = [r * assumptions.get("Other Income (% of Revenue)", {"Base": [0]*len(revenue)})[scenario][i] / 100 for i, r in enumerate(revenue)]
        other_exp = [r * assumptions.get("Other Expenses (% of Revenue)", {"Base": [0]*len(revenue)})[scenario][i] / 100 for i, r in enumerate(revenue)]
        depreciation = [r * assumptions["Depreciation (% of Revenue)"][scenario][i] / 100 for i, r in enumerate(revenue)]
        amortization = [0 for _ in revenue]  # Placeholder until full amortization logic is integrated
        ebitda = [revenue[i] - cogs[i] - admin_exp[i] - sales_exp[i] for i in range(len(revenue))]
        ebit = [ebitda[i] - depreciation[i] - amortization[i] for i in range(len(revenue))]

        # Dummy values until debt and cash logic are wired in
        interest_paid = [0] * len(revenue)
        interest_earned = [0] * len(revenue)

        ebt_pre_workers = [ebit[i] - interest_paid[i] + interest_earned[i] + other_inc[i] - other_exp[i] for i in range(len(revenue))]
        workers_participation = [0.15 * e for e in ebt_pre_workers]
        taxable_income = [ebt_pre_workers[i] - workers_participation[i] for i in range(len(revenue))]
        tax_rate = assumptions["Tax Rate (%)"][scenario]
        taxes = [taxable_income[i] * tax_rate[i] / 100 for i in range(len(revenue))]
        net_income = [taxable_income[i] - taxes[i] for i in range(len(revenue))]

        fcf = [net_income[i] + depreciation[i] + amortization[i]  # Non-cash addbacks
               - (revenue[i] * assumptions["CapEx (% of Revenue)"][scenario][i] / 100)  # CapEx
               - (revenue[i] * assumptions["Working Capital (% of Revenue)"][scenario][i] / 100)  # WC changes
               for i in range(len(revenue))]

        return pd.DataFrame({
            "Year": [datetime.now().year + i for i in range(len(revenue))],
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
            "Other Income": other_inc,
            "Other Expenses": other_exp,
            "EBT (Pre Workers)": ebt_pre_workers,
            "Workers Participation": workers_participation,
            "Taxable Income": taxable_income,
            "Taxes": taxes,
            "Net Income": net_income,
            "FCF": fcf
})

    for scenario in scenarios:
        revenue = [st.session_state["historical_data"].iloc[-1]["Revenue"]]
        for g in assumptions["Revenue Growth (%)"][scenario]:
            revenue.append(revenue[-1] * (1 + g / 100))
        revenue = revenue[1:]

        income_df = generate_income_statement(revenue, assumptions, scenario)
        income_df["Year"] = [datetime.now().year + i for i in range(st.session_state["years"])]

        projection_data[scenario] = income_df
        st.write(f"### {scenario} Scenario - Income Statement")
        st.dataframe(income_df.set_index("Year").T)

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