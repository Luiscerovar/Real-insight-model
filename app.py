import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Real Insight Financial Model", layout="wide")
st.title("📊 Real Insight Financial Model")

st.markdown("""
This tool helps model debt structures including:
- Multiple loan tranches
- Refinancing
- Balloon payments
- Cash flow-linked amortization
""")

# Input Section
st.header("📝 Loan Input Configuration")

with st.expander("Loan Tranches"):
    num_tranches = st.number_input("Number of Tranches", 1, 10, 2)
    tranches = []
    for i in range(num_tranches):
        st.subheader(f"Tranche {i+1}")
        amount = st.number_input(f"Amount (Tranche {i+1})", min_value=0.0, step=1000.0, key=f"amount_{i}")
        rate = st.number_input(f"Interest Rate % (Tranche {i+1})", min_value=0.0, max_value=100.0, value=8.0, key=f"rate_{i}")
        years = st.number_input(f"Term (years) (Tranche {i+1})", 1, 30, 5, key=f"years_{i}")
        start_year = st.number_input(f"Disbursement Year (Tranche {i+1})", 0, 10, i, key=f"start_{i}")
        method = st.selectbox(f"Amortization Method (Tranche {i+1})", ["Francesa", "Alemana", "Americana"], key=f"method_{i}")
        balloon = st.number_input(f"Balloon % at maturity (Tranche {i+1})", 0.0, 100.0, 0.0, key=f"balloon_{i}")
        tranches.append({
            "amount": amount, "rate": rate/100, "years": years,
            "start_year": start_year, "method": method, "balloon": balloon / 100
        })

# Projection Setup
years = list(range(0, 15))
cf_data = pd.DataFrame(index=years)
cf_data["Operating Cash Flow"] = 100000  # Dummy value

# Amortization Schedule + Cash Flow Impact
for idx, loan in enumerate(tranches):
    prefix = f"T{idx+1}"
    principal = loan["amount"]
    rate = loan["rate"]
    term = loan["years"]
    start = loan["start_year"]
    method = loan["method"]
    balloon = loan["balloon"]
    for t in range(term):
        year = start + t
        if method == "Francesa":
            pmt = np.pmt(rate, term, -principal)
            interest = np.ipmt(rate, t+1, term, -principal)
            principal_payment = pmt - interest
        elif method == "Alemana":
            principal_payment = principal / term
            interest = (principal - principal_payment * t) * rate
            pmt = principal_payment + interest
        elif method == "Americana":
            interest = principal * rate if t < term-1 else principal * rate
            principal_payment = 0 if t < term-1 else principal * (1 - balloon)
            pmt = principal_payment + interest
        cf_data.loc[year, f"{prefix} Interest"] = cf_data.get(f"{prefix} Interest", 0) + interest
        cf_data.loc[year, f"{prefix} Principal"] = cf_data.get(f"{prefix} Principal", 0) + principal_payment
        if balloon > 0 and t == term-1:
            cf_data.loc[year, f"{prefix} Balloon"] = principal * balloon

# Summarize Cash Flows
cf_data["Total Debt Service"] = cf_data.filter(like="Interest").sum(axis=1) + cf_data.filter(like="Principal").sum(axis=1) + cf_data.filter(like="Balloon").sum(axis=1)
cf_data["Net Cash Flow"] = cf_data["Operating Cash Flow"] - cf_data["Total Debt Service"]

# Output
st.header("📈 Cash Flow Projection")
st.dataframe(cf_data.fillna(0).style.format("{:,.0f}"))

st.line_chart(cf_data[["Operating Cash Flow", "Total Debt Service", "Net Cash Flow"]].fillna(0))
