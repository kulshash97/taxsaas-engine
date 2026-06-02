import streamlit as st
import pandas as pd
import re
from pypdf import PdfReader

# =====================================================================
# PLATFORM SETUPS & CUSTOM LAYOUT
# =====================================================================
st.set_page_config(
    page_title="Kulkarni Strategic Partners | Platform Suite", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- ENGINE A: UNIVERSAL BANK STATEMENT INFLOW PARSER ---
def parse_universal_bank_statement(file_buffered):
    """
    Universally extracts professional/business credit inflows across any Indian bank statement layout.
    Filters out running balances and debit transactions dynamically using adaptive keyword profiling.
    """
    total_credits = 0.0
    account_name = "Unknown Client"
    
    try:
        reader = PdfReader(file_buffered)
        full_text_dump = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text_dump += text + "\n"
                
        # Universal Name Extraction Profile
        name_match = re.search(r'(?:Account Name|Name|Customer Name)\s*["\s:]*([A-Z\s\.]{4,50})', full_text_dump, re.IGNORECASE)
        if name_match:
            account_name = name_match.group(1).strip().split('\n')[0].replace('"', '').strip()

        lines = full_text_dump.split('\n')
        for line in lines:
            line_clean = line.strip()
            
            # Universal Skip Filters (Headers, summaries, or metadata instructions)
            if any(x in line_clean.lower() for x in ["page", "date range", "opening balance", "closing balance", "summary"]):
                continue
            
            # Explicit Debit Elimination Filter (Prevents outflows from being misclassified as inflows)
            if any(dr_flag in line_clean.upper() for dr_flag in ["(DR)", " DEBIT ", "WITHDRAWAL", " CHQ ", "-"]):
                if not any(cr_flag in line_clean.upper() for cr_flag in ["(CR)", "CREDIT"]):
                    continue # Skip pure debits completely
            
            # Identify all decimal amounts representing financial volumes
            amounts = re.findall(r'(\d[\d,]*\.\d{2})', line_clean)
            if not amounts:
                continue
                
            # If line is verified to have a credit component or is a standard UPI/Inward deposit
            if any(cr_flag in line_clean.upper() for cr_flag in ["(CR)", "CREDIT", "CR/"]) or "UPI/" in line_clean.upper() or "NEFT" in line_clean.upper() or "RTGS" in line_clean.upper():
                # Convert string items to floats safely
                parsed_vals = [float(val.replace(',', '')) for val in amounts]
                
                if len(parsed_vals) >= 2:
                    # In almost all double-column layouts (HDFC, SBI, Union, ICICI):
                    # The transaction amount appears BEFORE the remaining running account balance.
                    # We pick the smaller or first token, ensuring the massive running balance isn't ingested.
                    if line_clean.count("(Cr)") == 2 or "BALANCE" in line_clean.upper() or parsed_vals[1] > parsed_vals[0]*3:
                        total_credits += parsed_vals[0]
                    else:
                        total_credits += parsed_vals[0]
                elif len(parsed_vals) == 1:
                    total_credits += parsed_vals[0]
                    
        return round(total_credits, 2), account_name
    except Exception as e:
        st.error(f"Bank Statement Ingestion Failure: {str(e)}")
        return 0.0, "Parsing Error State"


# --- ENGINE B: AUTOMATED AIS (ANNUAL INFORMATION STATEMENT) EXTRACTION CORE ---
def parse_income_tax_ais(file_buffered):
    """
    Ingests official Annual Information Statement (AIS) documents.
    Scans for high-value investment signatures (Mutual Funds, Equities, High Real Estate, SFTs).
    """
    detected_high_value_investments = 0.0
    ais_signatures_found = []
    
    try:
        reader = PdfReader(file_buffered)
        ais_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                ais_text += t + "\n"
        
        # Look for SFT patterns or Investment Summary metrics
        # Standard AIS forms lay out sections for SFT-005, SFT-006 (Mutual Funds, Stocks, Dividends)
        investment_patterns = [
            (r'(?:Purchase of mutual fund|Mutual Fund)\s+.*?(\d[\d,]*\.\d{2}|\d[\d,]+)', "Mutual Fund Ingestion"),
            (r'(?:Purchase of shares|Equities|Stocks)\s+.*?(\d[\d,]*\.\d{2}|\d[\d,]+)', "Equity Market Placement"),
            (r'(?:Sale/Purchase of immovable property)\s+.*?(\d[\d,]*\.\d{2}|\d[\d,]+)', "Real Estate Footprint"),
            (r'(?:SFT-\d{3})\s+.*?(\d[\d,]*\.\d{2}|\d[\d,]+)', "Specified Financial Transaction (SFT)")
        ]
        
        for pattern, label in investment_patterns:
            matches = re.finditer(pattern, ais_text, re.IGNORECASE)
            for match in matches:
                amt_str = match.group(1).replace(',', '')
                if '.' not in amt_str:
                    val = float(amt_str)
                else:
                    val = float(amt_str)
                
                if val > 50000: # Highlight material high value components
                    detected_high_value_investments += val
                    ais_signatures_found.append(f"Found {label}: ₹{val:,}")
                    
        # Fallback broad search if specific labels are tightly structured in tabular format
        if detected_high_value_investments == 0.0:
            # Check for generic continuous text numbers tagged under summary definitions
            summary_match = re.findall(r'(?:Total Value|Aggregate Value|Amount/Value)\s*[:]*\s*(\d[\d,]{4,})', ais_text, re.IGNORECASE)
            if summary_match:
                for match in summary_match[:2]: # Grab primary key components
                    val = float(match.replace(',', ''))
                    detected_high_value_investments += val
                    ais_signatures_found.append(f"Aggregate AIS Financial Signal: ₹{val:,}")

        return round(detected_high_value_investments, 2), ais_signatures_found
    except Exception as e:
        st.error(f"AIS Extraction Pipeline Failure: {str(e)}")
        return 0.0, []


# --- CORE STATUTORY MATHEMATICAL MODEL ---
def compute_progressive_tax_2026(taxable_profit):
    if taxable_profit <= 0:
        return 0.0, 0.0, 0.0
    
    slabs = [
        (400000, 0.00), (800000, 0.05), (1200000, 0.10),
        (1600000, 0.15), (2000000, 0.20), (2400000, 0.25),
        (float('inf'), 0.30)
    ]
    
    calculated_slab_tax = 0.0
    lower_bound = 0
    residual_income = taxable_profit

    for upper_bound, rate in slabs:
        segment_capacity = upper_bound - lower_bound
        if residual_income > segment_capacity:
            calculated_slab_tax += segment_capacity * rate
            residual_income -= segment_capacity
            lower_bound = upper_bound
        else:
            calculated_slab_tax += residual_income * rate
            break

    statutory_rebate = 0.0
    if taxable_profit <= 1200000:
        statutory_rebate = min(calculated_slab_tax, 60000.0)
    
    net_pre_cess = max(0.0, calculated_slab_tax - statutory_rebate)
    education_cess = net_pre_cess * 0.04
    aggregate_liability = net_pre_cess + education_cess
    
    return round(calculated_slab_tax, 2), round(statutory_rebate, 2), round(aggregate_liability, 2)


# =====================================================================
# ENTERPRISE GATEWAY AUTHORIZATION AUTH
# =====================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Kulkarni Strategic Partners | Secure Node Login")
    col_login, _ = st.columns([1.2, 2])
    with col_login:
        input_user = st.text_input("Node Username", value="admin_shashank")
        input_pass = st.text_input("Node Security Key", type="password", value="shashank123")
        if st.button("Authorize Node Connection", use_container_width=True):
            if input_user == "admin_shashank" and input_pass == "shashank123":
                st.session_state["authenticated"] = True
                st.session_state["node_user"] = "admin_shashank"
                st.rerun()
    st.stop()


# =====================================================================
# CORE WORKSPACE & WORKFLOW ENGINE
# =====================================================================
st.sidebar.markdown(f"🟢 **Active Node User:** `{st.session_state['node_user']}`")
if st.sidebar.button("🧹 Wipe Session Data Core", use_container_width=True):
    st.session_state.clear()
    st.rerun()

st.header("🚀 Universal Smart ITR Filing & AIS Cross-Reconciliation Core")
st.caption("Filing Engine Core | Multi-Bank Schema Adaptive Engine | Income Tax Act, 1961 Compliance Framework")

panel_left, panel_right = st.columns([1, 1])

extracted_turnover = 0.0
extracted_ais_investments = 0.0
client_name = "Not Identified"
ais_logs = []

with panel_left:
    st.subheader("📥 Data Ingestion Hub")
    
    # 1. Multi-Bank Universal File Drop
    uploaded_statement = st.file_uploader("Upload Client Bank Statement (Supports HDFC, ICICI, SBI, UBI, etc.)", type=["pdf"], key="bank_file")
    if uploaded_statement:
        extracted_turnover, client_name = parse_universal_bank_statement(uploaded_statement)
        st.success(f"🔗 Bank Matrix Synced! Profile Identity: **{client_name}**")
        st.metric(label="Isolated Real Ledger Deposits", value=f"₹{extracted_turnover:,}")
        
    st.markdown("---")
    
    # 2. Automated AIS Document Drop
    uploaded_ais = st.file_uploader("Upload Client Annual Information Statement (AIS) PDF", type=["pdf"], key="ais_file")
    if uploaded_ais:
        extracted_ais_investments, ais_logs = parse_income_tax_ais(uploaded_ais)
        st.info("📑 AIS Intelligence Vector Calculated!")
        st.metric(label="Identified AIS Asset Investments", value=f"₹{extracted_ais_investments:,}")
        for log in ais_logs:
            st.caption(f"📍 {log}")

    st.markdown("---")
    st.subheader("⚙️ Adjusted Data Control Panel")
    final_inflow = st.number_input("Verified Gross Turnovers (INR)", min_value=0.0, value=float(extracted_turnover))
    final_ais_val = st.number_input("High Value AIS Footprints Added (INR)", min_value=0.0, value=float(extracted_ais_investments))

with panel_right:
    st.subheader("🤖 Smart Compliance Agent Pipeline Matrix")
    
    if final_inflow == 0.0:
        st.info("👋 **Waiting for Ingestion:** Upload files into the Data Ingestion Hub to spin up calculations.")
    else:
        # Agent 1: Selecting the route
        with st.expander("🔹 Agent 1: Statutory Route Optimizer", expanded=True):
            if final_inflow <= 7500000:
                net_profit = final_inflow * 0.50
                route_tag = "Section 44ADA (Professional Presumptive)"
            else:
                net_profit = final_inflow * 0.06
                route_tag = "Section 44AD (Business Presumptive)"
            st.info(f"Filing Path Alignment: **{route_tag}**")
            st.write(f"Taxable Presumptive Profit: **₹{net_profit:,}**")

        # Agent 2: Computing taxes
        with st.expander("🔹 Agent 2: Tax Calculation Matrix", expanded=True):
            slab_tax, rebate_87a, total_tax = compute_progressive_tax_2026(net_profit)
            st.metric(label="Net System Tax Demand Liability", value=f"₹{total_tax:,}")
            
            breakdown_df = pd.DataFrame({
                "Tax Parameter Slabs": ["Calculated Gross Tax", "Sec 87A Rebate Absorbed", "Final Portal Balance Due"],
                "Amount (INR)": [f"₹{slab_tax:,}", f"₹{rebate_87a:,}", f"₹{total_tax:,}"]
            })
            st.table(breakdown_df)

        # Agent 3: Smart Risk Mitigation Engine
        with st.expander("⚠️ Agent 3: System Risk Auditing & AIS Reconciliation", expanded=True):
            if final_ais_val > net_profit:
                variance = final_ais_val - net_profit
                st.error("🚨 HIGH DISCREPANCY MISMATCH")
                st.write(f"The client invested **₹{final_ais_val:,}** in high-value assets according to the AIS. However, their declared net income is only **₹{net_profit:,}**.")
                st.warning(f"⚠️ Unexplained Gap: **₹{variance:,}**. Filing now will highly trigger an IT Department scrutiny notice under section 143(1) / 148.")
            else:
                st.success("✅ Risk analysis cleared. High-value investments line up completely with the declared business earnings safely.")

# --- MANIFEST PRODUCTION OUTPUT ---
if final_inflow > 0.0:
    st.markdown("---")
    report_html = f"""
    <html>
    <head><style>body {{ font-family: sans-serif; padding: 20px; }} .box {{ background: #F8FAFC; border-left: 5px solid #1E3A8A; padding: 15px; }}</style></head>
    <body>
        <h2>OFFICIAL RECONCILIATION SUMMARY REPORT</h2>
        <div class="box">
            <strong>Client Name:</strong> {client_name}<br>
            <strong>Total Calculated Bank Deposits:</strong> ₹{final_inflow:,}<br>
            <strong>Total Traced Asset Footprints (AIS):</strong> ₹{final_ais_val:,}<br>
            <strong>Assigned Path:</strong> {route_tag}<br>
            <strong>Tax Payable Demand:</strong> ₹{total_tax:,}
        </div>
    </body>
    </html>
    """
    st.download_button("📥 Download Finalized Filing Manifest Blueprint", data=report_html, file_name="Filing_Manifest.html", mime="text/html", use_container_width=True)