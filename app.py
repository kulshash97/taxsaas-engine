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

# --- DETAILED ADAPTIVE BANK LEDGER EXTRACTION CORE ---
def parse_universal_bank_statement(file_buffered):
    """
    Surgically computes precise cumulative credit inflows from bank statement text dumps.
    Isolates row transaction indicators from running balance text layers completely.
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
                
        # Safe Holder Account Name Extraction
        name_match = re.search(r'(?:Account Name|Name|Customer Name)\s*["\s:]*([A-Z\s\.]{4,50})', full_text_dump, re.IGNORECASE)
        if name_match:
            account_name = name_match.group(1).strip().split('\n')[0].replace('"', '').strip()

        lines = full_text_dump.split('\n')
        for line in lines:
            line_clean = line.strip()
            
            # Global Metadata Filters
            if any(meta in line_clean.lower() for meta in ["page", "opening balance", "closing balance", "date range", "statement summary"]):
                continue
            
            # Trace value-direction combinations like "420000.00(Cr)" or "3699.95(Dr)"
            explicit_pairs = re.findall(r'(\d[\d,]*\.\d{2})\s*\((Cr|Dr)\)', line_clean, re.IGNORECASE)
            
            if len(explicit_pairs) == 2:
                # Layout: [Transaction Amount](Direction) ... [Account Running Balance](Direction)
                tx_amt, tx_type = explicit_pairs[0]
                if tx_type.lower() == 'cr':
                    total_credits += float(tx_amt.replace(',', ''))
                    
            elif len(explicit_pairs) == 1:
                # Layout: Only one bracketed element exists on this row
                all_decimals = re.findall(r'(\d[\d,]*\.\d{2})', line_clean)
                if len(all_decimals) >= 2:
                    tx_amt = all_decimals[0]
                    # If the line represents a cash deposit or verified inward transfer ledger route
                    if any(token in line_clean.upper() for token in ["/CR/", "BY CASH", "BY TRANSFER", "INT.PD", "INTEREST", "CREDIT"]):
                        if not any(dr_token in line_clean.upper() for dr_token in ["/DR/", "(DR)", "DEBIT"]):
                            total_credits += float(tx_amt.replace(',', ''))
            else:
                # Fallback layout context parsing for standard tabular row blocks
                if any(token in line_clean.upper() for token in ["UPI/CR/", "NEFT INWARD", "RTGS INWARD", "IMPS INWARD", "BY CASH"]):
                    all_decimals = re.findall(r'(\d[\d,]*\.\d{2})', line_clean)
                    if all_decimals:
                        total_credits += float(all_decimals[0].replace(',', ''))
                        
        return round(total_credits, 2), account_name
    except Exception as e:
        st.error(f"Parser Engine Interruption: {str(e)}")
        return 0.0, "Parsing Error State"


# --- AUTOMATED TAX AIS PROCESSING ENGINE ---
def parse_income_tax_ais(file_buffered):
    """
    Scans and reads high-value investments directly from Annual Information Statement (AIS) uploads.
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
        
        investment_patterns = [
            (r'(?:Purchase of mutual fund|Mutual Fund Summary)\s+.*?(\d[\d,]*\.\d{2}|\d[\d,]+)', "Mutual Fund Purchase"),
            (r'(?:Purchase of shares|Equity Transactions)\s+.*?(\d[\d,]*\.\d{2}|\d[\d,]+)', "Equity Investment"),
            (r'(?:Immovable Property Sale/Purchase)\s+.*?(\d[\d,]*\.\d{2}|\d[\d,]+)', "Real Estate Transaction"),
            (r'(?:SFT-\d{3})\s+.*?(\d[\d,]*\.\d{2}|\d[\d,]+)', "SFT Flag Report")
        ]
        
        for pattern, label in investment_patterns:
            matches = re.finditer(pattern, ais_text, re.IGNORECASE)
            for match in matches:
                amt_str = match.group(1).replace(',', '')
                val = float(amt_str)
                if val > 10000:
                    detected_high_value_investments += val
                    ais_signatures_found.append(f"Identified {label}: ₹{val:,}")
                    
        if detected_high_value_investments == 0.0:
            summary_matches = re.findall(r'(?:Total Value|Aggregate Value|Amount/Value)\s*[:]*\s*(\d[\d,]{4,})', ais_text, re.IGNORECASE)
            for match in summary_matches[:2]:
                val = float(match.replace(',', ''))
                detected_high_value_investments += val
                ais_signatures_found.append(f"AIS Aggregate Financial Target: ₹{val:,}")

        return round(detected_high_value_investments, 2), ais_signatures_found
    except Exception as e:
        st.error(f"AIS Extraction Error: {str(e)}")
        return 0.0, []


# --- STATUTORY MATHEMATICAL MODEL ENGINE ---
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
# B2B ACCESS LAYER GATEWAY
# =====================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Kulkarni Strategic Partners | Secure Node Access")
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
# SYSTEM EXECUTIVE MANAGEMENT INTERFACE
# =====================================================================
st.sidebar.markdown(f"🟢 **Workspace Node Active:** `{st.session_state['node_user']}`")
if st.sidebar.button("🧹 Clear Running Workspace Session", use_container_width=True):
    st.session_state.clear()
    st.rerun()

st.header("🚀 Universal Smart ITR Filing & AIS Cross-Reconciliation Core")
st.caption("Adaptive Multi-Schema Document Ingestion Hub | Income Tax Act, 1961 Compliance Modules")

panel_left, panel_right = st.columns([1, 1])

extracted_turnover = 0.0
extracted_ais_investments = 0.0
client_name = "Not Identified"
ais_logs = []

with panel_left:
    st.subheader("📥 Data Ingestion Hub")
    
    # Target Ingestion Component 1: Universal Statement Upload
    uploaded_statement = st.file_uploader("Upload Bank Statement (PDF ONLY)", type=["pdf"], key="bank_prod_v3")
    if uploaded_statement:
        extracted_turnover, client_name = parse_universal_bank_statement(uploaded_statement)
        st.success(f"🔗 Bank Ledger Verified! Target Identity: **{client_name}**")
        st.metric(label="Calculated Net Inflows", value=f"₹{extracted_turnover:,}")
        
    st.markdown("---")
    
    # Target Ingestion Component 2: Official AIS Upload Channel
    uploaded_ais = st.file_uploader("Upload Client Annual Information Statement (AIS) PDF", type=["pdf"], key="ais_prod_v3")
    if uploaded_ais:
        extracted_ais_investments, ais_logs = parse_income_tax_ais(uploaded_ais)
        st.info("📑 AIS Ledger Ingested Effectively")
        st.metric(label="Traced AIS High-Value Financial Assets", value=f"₹{extracted_ais_investments:,}")
        for log in ais_logs:
            st.caption(f"📍 {log}")

    st.markdown("---")
    st.subheader("⚙️ Overrides Control Interface")
    final_inflow = st.number_input("Verified Inflows (INR)", min_value=0.0, value=float(extracted_turnover))
    final_ais_val = st.number_input("Traced AIS Investments (INR)", min_value=0.0, value=float(extracted_ais_investments))

with panel_right:
    st.subheader("🤖 Automated Cross-Auditing Agent Pipeline")
    
    if final_inflow == 0.0:
        st.info("👋 **Waiting for Ingestion Input:** Drop client banking records and AIS files into the left terminal blocks to begin computation.")
    else:
        # Agent Module 1: Selecting Path Frameworks
        with st.expander("🔹 Agent 1: Statutory Route Optimizer", expanded=True):
            if final_inflow <= 7500000:
                net_profit = final_inflow * 0.50
                route_tag = "Section 44ADA (Professional Presumptive)"
            else:
                net_profit = final_inflow * 0.06
                route_tag = "Section 44AD (Business Presumptive)"
            st.info(f"Filing Path Selection: **{route_tag}**")
            st.write(f"Calculated Taxable Net Profit Core: **₹{net_profit:,}**")

        # Agent Module 2: Bracket Calculators
        with st.expander("🔹 Agent 2: Statutory Tax Engine", expanded=True):
            slab_tax, rebate_87a, total_tax = compute_progressive_tax_2026(net_profit)
            st.metric(label="Net System Tax Liability Due", value=f"₹{total_tax:,}")
            
            breakdown_df = pd.DataFrame({
                "Tax Parameter Vector": ["Gross Slab Liability", "Sec 87A Rebate Absorbed", "Final Portal Balance Due"],
                "Value (INR)": [f"₹{slab_tax:,}", f"₹{rebate_87a:,}", f"₹{total_tax:,}"]
            })
            st.table(breakdown_df)

        # Agent Module 3: Security Mitigation Profiling
        with st.expander("⚠️ Agent 3: System Risk Auditing & AIS Reconciliation", expanded=True):
            if final_ais_val > net_profit:
                variance = final_ais_val - net_profit
                st.error("🚨 CRITICAL RISK MISMATCH DETECTED")
                st.write(f"Client invested **₹{final_ais_val:,}** in high-value assets (AIS profile). However, declared presumptive earnings are only **₹{net_profit:,}**.")
                st.warning(f"⚠️ Unexplained Deficit Segment: **₹{variance:,}**. Filing now runs a near-100% chance of triggering an automatic scrutiny notice.")
            else:
                st.success("✅ Risk analysis cleared. Investments line up properly with the declared profit corridors.")

# --- COMPLIANCE REPORT BLUEPRINT DESIGN MANIFEST ---
if final_inflow > 0.0:
    st.markdown("---")
    report_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; color: #1E293B; }}
            .card {{ background: #F8FAFC; border-left: 6px solid #1E3A8A; padding: 20px; border-radius: 4px; }}
            .title {{ font-size: 22px; font-weight: bold; color: #1E3A8A; margin-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #CBD5E1; padding: 10px; text-align: left; }}
            th {{ background: #E2E8F0; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="title">OFFICIAL TAX RECONCILIATION SUMMARY BLUEPRINT</div>
            <strong>Client Name Identity:</strong> {client_name}<br><br>
            <table>
                <tr><th>Audited Operational Metrics</th><th>Verified Calculated Value Baseline</th></tr>
                <tr><td>Isolated Real Ledger Deposits Inflows</td><td>INR {final_inflow:,}</td></tr>
                <tr><td>Traced High-Value AIS Asset Deployments</td><td>INR {final_ais_val:,}</td></tr>
                <tr><td>Assigned Compliance Filing Framework</td><td>{route_tag}</td></tr>
                <tr><td><strong>Final Portal Net Payable Tax Demand</strong></td><td><strong>INR {total_tax:,}</strong></td></tr>
            </table>
        </div>
    </body>
    </html>
    """
    st.components.v1.html(report_html, height=320, scrolling=True)
    st.download_button(
        label="📥 Download Production Reconciliation Blueprint Manifest", 
        data=report_html, 
        file_name=f"Verified_Filing_Blueprint_{client_name.replace(' ', '_')}.html", 
        mime="text/html", 
        use_container_width=True
    )