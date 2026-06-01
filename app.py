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

# --- LIVE OCR & BANKING TRANSACTION EXTRACTION ENGINE ---
def parse_live_bank_statement(file_buffered):
    """
    Reads the actual PDF file lines, extracts the legal account holder name,
    and isolates genuine Credit Inflows by filtering out trailing Running Balances.
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
        
        # 1. Dynamic Client Name Extraction Loop
        name_match = re.search(r'(?:Account Name|Name)\s*["\s:]*([A-Z\s]{4,50})', full_text_dump, re.IGNORECASE)
        if name_match:
            extracted_name = name_match.group(1).strip()
            # Clean out multi-line address or garbage tokens from table headers
            account_name = extracted_name.split('\n')[0].replace('"', '').strip()

        # 2. Extract and Sum Real Credit Transactions Only
        lines = full_text_dump.split('\n')
        for line in lines:
            # Check if the line contains a transaction trace
            if "(Cr)" in line or "(Dr)" in line:
                # Find all currency/numeric strings on this line
                all_amounts = re.findall(r'(\d[\d,]*\.\d{2})', line)
                
                if all_amounts:
                    # In a typical row: the last number is ALWAYS the running balance column.
                    # We pop it out so it is NEVER added to our income calculations.
                    running_balance = all_amounts[-1]
                    remaining_numbers = all_amounts[:-1]
                    
                    # If there's a number left and the line explicitly flags a transaction credit line
                    # Look for the transaction indicator right next to the value
                    if remaining_numbers:
                        target_inflow = remaining_numbers[-1].replace(',', '')
                        # Confirm that this specific row transaction was a Credit, not a Debit
                        # It must have '(Cr)' positioned before the running balance string segment
                        balance_idx = line.find(running_balance)
                        inflow_segment = line[:balance_idx]
                        
                        if "(Cr)" in inflow_segment:
                            try:
                                total_credits += float(target_inflow)
                            except ValueError:
                                continue
                                
        return round(total_credits, 2), account_name
    except Exception as e:
        st.error(f"OCR Parsing Exception: Unable to compute ledger file safely. Error details: {str(e)}")
        return 0.0, "Parsing Error State"


# --- CORE MATH MODULE FOR COMPLIANCE (AGENT 3 CORE) ---
def compute_progressive_tax_2026(taxable_profit):
    if taxable_profit <= 0:
        return 0.0, 0.0, 0.0
    
    slabs = [
        (400000, 0.00),       # Up to 4,00,000: NIL
        (800000, 0.05),       # 4,00,001 to 8,00,000: 5%
        (1200000, 0.10),      # 8,00,001 to 12,00,000: 10%
        (1600000, 0.15),      # 12,00,001 to 16,00,000: 15%
        (2000000, 0.20),      # 16,00,001 to 20,00,000: 20%
        (2400000, 0.25),      # 20,00,001 to 24,00,000: 25%
        (float('inf'), 0.30)  # Above 24,00,000: 30%
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
# ENTERPRISE B2B AUTHENTICATION GATEWAY
# =====================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "node_user" not in st.session_state:
    st.session_state["node_user"] = ""
if "enterprise_name" not in st.session_state:
    st.session_state["enterprise_name"] = ""
if "partner_tier" not in st.session_state:
    st.session_state["partner_tier"] = ""

if not st.session_state["authenticated"]:
    st.title("🔒 Kulkarni Strategic Partners | Secure Node Login")
    st.caption("Enterprise B2B Decentralized Authorization Console")
    
    col_login, _ = st.columns([1.2, 2])
    with col_login:
        st.info("💡 **B2B Tenant Provisioning:** Use default system clearance keys.")
        input_user = st.text_input("Node Username / Operator Token", value="admin_shashank")
        input_pass = st.text_input("Node Security Key / Password", type="password", value="shashank123")
        
        if st.button("Authorize Node Connection", use_container_width=True):
            if input_user == "admin_shashank" and input_pass == "shashank123":
                st.session_state["authenticated"] = True
                st.session_state["node_user"] = "admin_shashank"
                st.session_state["enterprise_name"] = "KULKARNI STRATEGIC PARTNERS"
                st.session_state["partner_tier"] = "👑 Elite Partner Tier"
                st.rerun()
            else:
                st.error("🚨 Invalid Tenant Token credentials. Authorization denied.")
    st.stop()


# =====================================================================
# SIDEBAR NAVIGATION INTERFACE
# =====================================================================
st.sidebar.markdown(f"🟢 **Node:** `{st.session_state['node_user']}`")
st.sidebar.markdown(f"🏢 **Enterprise:** `{st.session_state['enterprise_name']}`")
st.sidebar.markdown(f"📈 **Tier:** {st.session_state['partner_tier']}")

if st.sidebar.button("🧹 Clear All Session Cache & Slate", use_container_width=True):
    st.session_state.pop("uploaded_inflow", None)
    st.session_state.pop("extracted_client_name", None)
    st.toast("Wiped local memory stacks completely clean.", icon="🗑️")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ PLATFORM MODULES")
selected_module = st.sidebar.radio("Select Platform Track to Execute:", ["🚀 Module 1: Smart ITR Filing Engine"])

# =====================================================================
# FILING ENGINE REAL DATA PIPELINE
# =====================================================================
if selected_module == "🚀 Module 1: Smart ITR Filing Engine":
    st.header("🚀 Module 1: Smart ITR Filing Engine (Live Separation Core)")
    st.caption("Filing Engine Core | Statutory Alignment: Income Tax Act, 1961")
    
    panel_left, panel_right = st.columns([1, 1])
    
    extracted_turnover = 0.0
    client_name = "Not Identified"
    
    with panel_left:
        st.subheader("📥 Data Ingestion Hub")
        uploaded_statement = st.file_uploader("Upload Bank Statement (PDF ONLY)", type=["pdf"])
        
        if uploaded_statement is not None:
            extracted_turnover, client_name = parse_live_bank_statement(uploaded_statement)
            if extracted_turnover > 0:
                st.success(f"🔗 OCR Match Found! Client Identified: **{client_name}**")
            else:
                st.warning("⚠️ Scanned PDF contains zero explicit credit entries or text layer is non-readable images.")
        
        final_inflow = st.number_input("Gross Account Inflows Verified (INR)", min_value=0.0, value=float(extracted_turnover), step=5000.0)
        cash_ratio = st.slider("Cash Component Ratio (%)", min_value=0, max_value=100, value=0)
        ais_input_val = st.number_input("Enter Actual AIS High Value Investment Figure (INR)", min_value=0.0, value=0.0, step=5000.0)

    with panel_right:
        st.subheader("🤖 Real-Time Agent Matrix Pipeline")
        
        if final_inflow == 0.0:
            st.info("👋 **System Idle Baseline:** Please drag and drop a valid banking ledger PDF to run tax calculations. No mock numbers are active.")
            route_tag, net_profit, slab_tax, rebate_87a, total_tax, risk_status, risk_notes, variance_amt = "N/A", 0, 0, 0, 0, "Clean", "No active data", 0
        else:
            # Agent 1: Banking Ledger Vectorizer
            with st.expander("🔹 Agent 1: Banking Ledger Vectorizer", expanded=True):
                st.write(f"Account Legal Identity Holder: **{client_name}**")
                st.write(f"Verified gross receipts isolated from raw text strings: **₹{final_inflow:,}**")
                
            # Agent 2: Statutory Business Path Router
            with st.expander("🔹 Agent 2: Statutory Route Optimizer", expanded=True):
                if final_inflow <= 7500000:
                    net_profit = final_inflow * 0.50
                    route_tag = "Section 44ADA"
                else:
                    net_profit = final_inflow * 0.06
                    route_tag = "Section 44AD"
                st.info(f"✅ Route Selected: **{route_tag}**.")
                st.write(f"Calculated Taxable Presumptive Net Profit: **₹{net_profit:,}**")

            # Agent 3: Progressive Slab Engine
            with st.expander("🔹 Agent 3: Tax Computation Core", expanded=True):
                slab_tax, rebate_87a, total_tax = compute_progressive_tax_2026(net_profit)
                st.metric(label="Calculated Net Tax Demand (Inc. Cess)", value=f"₹{total_tax:,}")
                
                breakdown_df = pd.DataFrame({
                    "Matrix Component Vector": ["Calculated Slab Liability", "Section 87A Rebate Absorbed", "Final Portal Balance"],
                    "Amount (INR)": [f"₹{slab_tax:,}", f"₹{rebate_87a:,}", f"₹{total_tax:,}"]
                })
                st.table(breakdown_df)

            # Agent 4: Risk Mitigation & AIS Tracker
            with st.expander("⚠️ Agent 4: Risk Mitigation & AIS Reconciliation", expanded=True):
                variance_amt = max(0.0, ais_input_val - net_profit)
                if ais_input_val > net_profit:
                    risk_status = "High Risk Mismatch"
                    risk_notes = f"Asset investments of ₹{ais_input_val:,} exceed presumptive profit corridors by ₹{variance_amt:,}."
                    st.error("🚨 CRITICAL DISCREPANCY DETECTED")
                else:
                    risk_status = "Clean Pass"
                    risk_notes = "All listed transactions flow inside regular presumptive net profit bounds safely."
                    st.success("✅ Risk analysis metrics cleared.")

    # =====================================================================
    # INTERACTIVE SOURCE RECONCILIATION WORKSPACE 
    # =====================================================================
    selected_sources = []
    source_explanation_text = ""
    
    if final_inflow > 0.0 and ais_input_val > net_profit:
        st.markdown("---")
        st.subheader("🛡️ Source of Funds Reconciliation Workspace")
        st.warning(f"Verify how the client funded the **₹{variance_amt:,}** investment variance before executing portal steps:")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            s1 = st.checkbox("Past Accumulated Savings Accounts Trails Verified")
            s2 = st.checkbox("Redeemed Older Capital Assets / Matured FDs")
        with col_c2:
            s3 = st.checkbox("Tax-Free Family Gifts / Inheritance Received")
            s4 = st.checkbox("Exempt Income / Agricultural Revenue Inflows")
            
        if s1: selected_sources.append("Accumulated historical taxed savings pools.")
        if s2: selected_sources.append("Liquidation logs of older capital asset investments.")
        if s3: selected_sources.append("Tax-exempt blood relative gifts under Sec 56(2)(x).")
        if s4: selected_sources.append("Legally documented tax-free exempt earnings streams.")
        
        source_explanation_text = " ".join(selected_sources) if selected_sources else "[No source verification checked]"

    # --- NATIVE DYNAMIC REPORT MANIFEST ENGINE ---
    if final_inflow > 0.0:
        st.markdown("---")
        st.subheader("📄 Module 1: Comprehensive Step-by-Step Filing & Compliance Report Generator")
        
        report_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 25px; line-height: 1.6; color: #1E293B; }}
                .header {{ border-bottom: 4px solid #1E3A8A; padding-bottom: 12px; margin-bottom: 25px; }}
                .title {{ font-size: 26px; font-weight: bold; color: #1E3A8A; }}
                .meta {{ font-size: 13px; color: #475569; margin-bottom: 25px; background: #F1F5F9; padding: 12px; border-radius: 6px; }}
                .section {{ margin-bottom: 30px; padding: 20px; background: #F8FAFC; border-left: 5px solid #3B82F6; border-radius: 4px; }}
                .step {{ font-weight: bold; color: #0F172A; margin-top: 15px; font-size: 15px; text-transform: uppercase; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }}
                th, td {{ padding: 12px; border: 1px solid #CBD5E1; text-align: left; }}
                th {{ background: #E2E8F0; color: #0F172A; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">OFFICIAL TAX COMPLIANCE REPORT MANIFEST</div>
                <div style="font-size: 14px; color: #475569;">Kulkarni Strategic Partners Platform Suite</div>
            </div>
            
            <div class="meta">
                <strong>Assessed Client Identity Name:</strong> {client_name}<br>
                <strong>Authorized Node User:</strong> {st.session_state["node_user"]}<br>
                <strong>Enterprise Account Entity:</strong> {st.session_state["enterprise_name"]}
            </div>

            <div class="section">
                <h3>📊 Real Dynamic Financial Summary Matrix</h3>
                <table>
                    <tr><th>Audited Component Field</th><th>Computed Value Baseline</th></tr>
                    <tr><td>Filing Route Framework</td><td><strong>{route_tag}</strong></td></tr>
                    <tr><td>Actual Extracted Bank Ledger Inflows</td><td>INR {final_inflow:,}</td></tr>
                    <tr><td>Computed Net Business Profits</td><td>INR {net_profit:,}</td></tr>
                    <tr><td>Section 87A Relief applied</td><td>INR {rebate_87a:,}</td></tr>
                    <tr><td><strong>Final Portal Net Payable Tax Demand</strong></td><td><strong>INR {total_tax:,}</strong></td></tr>
                    <tr><td>Risk Status Evaluation Profile Flag</td><td><strong>{risk_status}</strong></td></tr>
                </table>
            </div>

            <div class="section">
                <h3>📑 Custom step-by-step E-Filing Portal Instructions</h3>
                <div class="step">STEP 1: Portal Entry</div>
                <p>Log into <u>incometax.gov.in</u> using the verified PAN credentials for <strong>{client_name}</strong>.</p>
                <div class="step">STEP 2: Value Fields Data Entry</div>
                <p>Open Schedule BP. Choose the commercial category and enter a gross revenue metric of exactly <strong>INR {final_inflow:,}</strong>, updating the net presumptive profit structure to <strong>INR {net_profit:,}</strong>.</p>
                <div class="step">STEP 3: Validate Final Slab Calculations</div>
                <p>Confirm on the computation breakdown ledger sheet that the net tax payable calculates precisely to the target metric of **INR {total_tax:,}** before validating and finalizing with Aadhaar OTP verification flows.</p>
            </div>
        </body>
        </html>
        """
        
        st.components.v1.html(report_html, height=500, scrolling=True)
        st.download_button(
            label="📥 Download Real Compliance Blueprint Manifest",
            data=report_html,
            file_name=f"Verified_Filing_Blueprint_{client_name.replace(' ', '_')}.html",
            mime="text/html",
            use_container_width=True
        )