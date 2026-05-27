import streamlit as st
import pandas as pd
import json
# Import the stable, synchronous data extraction engine
from fetch_engine import fetch_client_portal_data

# Set premium, institutional-grade page configuration
st.set_page_config(
    page_title="Kulkarni Strategic Partners | Enterprise Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Styles
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #64748B; margin-bottom: 2rem; }
    .card { background-color: #F8FAFC; padding: 1.5rem; border-radius: 0.5rem; border-left: 5px solid #2563EB; margin-bottom: 1rem; }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: #0F172A; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# CORE RECONCILIATION AUDIT ENGINE
# -------------------------------------------------------------------
def execute_system_reconciliation_audit(internal_ledger, portal_stream):
    """
    KSP Foundational Audit Module: Automatically reconciles internal client records 
    against live portal data arrays to flag structural variances.
    """
    audit_log = {
        "status": "PASS",
        "total_variance": 0.0,
        "flagged_exceptions": []
    }
    
    for invoice_id, internal_record in internal_ledger.items():
        portal_record = portal_stream.get(invoice_id)
        
        if not portal_record:
            audit_log["status"] = "FAIL"
            audit_log["flagged_exceptions"].append({
                "invoice": invoice_id,
                "error_type": "Missing Portal Record",
                "variance": internal_record['amount']
            })
            audit_log["total_variance"] += internal_record['amount']
            
        elif internal_record['tax_credit'] != portal_record['tax_credit']:
            variance = abs(internal_record['tax_credit'] - portal_record['tax_credit'])
            if variance > 0.05:  # Tolerance threshold parameter
                audit_log["status"] = "FAIL"
                audit_log["flagged_exceptions"].append({
                    "invoice": invoice_id,
                    "error_type": "Tax Credit Mismatch",
                    "variance": variance
                })
                audit_log["total_variance"] += variance
                
    return audit_log

# -------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=200&q=80", use_container_width=True)
    st.markdown("### **KSP Control Center**")
    app_mode = st.radio(
        "Select Enterprise Workspace:",
        ["1. Dual-Route Optimization", "2. System Reconciliation Audit", "3. Corporate Invoicing Engine"]
    )
    st.markdown("---")
    st.caption("Kulkarni Strategic Partners v1.0.0 | Operational Mode")

# -------------------------------------------------------------------
# WORKSPACE 1: DUAL-ROUTE OPTIMIZATION
# -------------------------------------------------------------------
if app_mode == "1. Dual-Route Optimization":
    st.markdown('<div class="main-header">Dual-Route Tax & Revenue Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Bain-grade client profile analysis tool</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### **Client Financial Parameters**")
        gross_turnover = st.number_input("Gross Annual Turnover (INR)", min_value=0.0, value=12500000.0, step=50000.0)
        declared_profit = st.number_input("Declared Net Business Profit (INR)", min_value=0.0, value=1500000.0, step=25000.0)
        digital_receipts_pct = st.slider("Percentage of Digital/Digital-Banking Receipts (%)", 0, 100, 95)
    
    with col2:
        st.markdown("### **Strategic Optimization Comparison**")
        
        # Presumptive taxation simulation under Section 44AD
        presumptive_rate = 0.06 if digital_receipts_pct >= 95 else 0.08
        simulated_presumptive_income = gross_turnover * presumptive_rate
        
        st.markdown(f"""
        <div class="card">
            <h4>Route A: Traditional Evaluation</h4>
            <p>Based on declared books of accounts.</p>
            <div class="metric-value">₹{declared_profit:,.2f}</div>
        </div>
        <div class="card">
            <h4>Route B: Presumptive Matrix Optimization</h4>
            <p>Optimized under statutory presumptive parameters ({presumptive_rate*100}% rate applied).</p>
            <div class="metric-value">₹{simulated_presumptive_income:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        tax_delta = declared_profit - simulated_presumptive_income
        if tax_delta > 0:
            st.success(f"🔥 Strategic Optimization Advantage Found: Reduce taxable base by ₹{tax_delta:,.2f} via Route B.")
        else:
            st.info("Route A remains optimal for this financial layout profile.")

# -------------------------------------------------------------------
# WORKSPACE 2: SYSTEM RECONCILIATION AUDIT (STABLE SYNC INTEGRATION)
# -------------------------------------------------------------------
elif app_mode == "2. System Reconciliation Audit":
    st.markdown('<div class="main-header">Automated System Audit Interface</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Internal control testing and ledger variance extraction</div>', unsafe_allow_html=True)
    
    st.markdown("### 🤖 **Automated Data Retrieval Control**")
    st.caption("Execute a stable background browser instance inside the main thread to securely pull data for ₹0 cost.")
    
    target_url = st.text_input("Target Secure Portal Login URL", "https://example-compliance-portal.in/login")
    
    c1, c2 = st.columns(2)
    with c1:
        portal_user = st.text_input("Portal Username ID")
    with c2:
        portal_pass = st.text_input("Portal Password Secure", type="password")
        
    if st.button("⚡ Run Background Portal Ingestion Script"):
        if not portal_user or not portal_pass:
            st.warning("Please enter valid portal credentials to initialize the browser session.")
        else:
            with st.spinner("Launching cloud-optimized synchronous browser instance via Playwright..."):
                # Call the synchronous function call directly
                extracted_data = fetch_client_portal_data(
                    target_url, portal_user, portal_pass, "#ledger-data-summary"
                )
                
                # 🛡️ SAFE CHECK: Ensure extracted_data is a dictionary and not None
                if isinstance(extracted_data, dict) and "status" in extracted_data:
                    if extracted_data["status"] == "SUCCESS":
                        st.success("🎉 Background Data Stream Retrieved Natively for ₹0!")
                        st.json(extracted_data)
                    else:
                        st.error(f"Execution Log Flagged: {extracted_data.get('error', 'Unknown extraction error')}")
                else:
                    st.error("❌ The background engine failed to launch or crashed unexpectedly. Check the 'Manage App' logs for browser binary initialization statuses.")
    
    # Structural verification ledger below
    mock_internal_ledger = {
        "INV-2026-001": {"amount": 50000.0, "tax_credit": 9000.0},
        "INV-2026-002": {"amount": 120000.0, "tax_credit": 21600.0},
        "INV-2026-003": {"amount": 75000.0, "tax_credit": 13500.0}
    }
    
    mock_portal_stream = {
        "INV-2026-001": {"amount": 50000.0, "tax_credit": 9000.0},
        "INV-2026-002": {"amount": 120000.0, "tax_credit": 18000.0},  # Engineered mismatch
    }
    
    st.markdown("### **Active Data Streams Flagged for Verification**")
    if st.button("Execute Core Reconciliation Audit Pipeline"):
        result = execute_system_reconciliation_audit(mock_internal_ledger, mock_portal_stream)
        
        if result["status"] == "FAIL":
            st.error(f"❌ System Audit Flags Tripped! Total Variance Extracted: ₹{result['total_variance']:,.2f}")
            df_exceptions = pd.DataFrame(result["flagged_exceptions"])
            st.dataframe(df_exceptions, use_container_width=True)
        else:
            st.success("✅ All data streams balanced perfectly. Zero variances found across the transaction matrix.")

# -------------------------------------------------------------------
# WORKSPACE 3: CORPORATE INVOICING ENGINE
# -------------------------------------------------------------------
elif app_mode == "3. Corporate Invoicing Engine":
    st.markdown('<div class="main-header">Day-1 Monetization Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate instant professional receipts for corporate advisory retainers</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### **Invoice Details**")
        client_name = st.text_input("Corporate Client Name", value="ABC Enterprises Ltd")
        service_desc = st.selectbox("Strategic Advisory Category", [
            "Corporate Financial Restructuring Matrix",
            "B2B Data Integration and Compliance Optimization Setup",
            "Institutional Portfolio Staggered Allocation Blueprint"
        ])
        retainer_fee = st.number_input("Advisory Fee Amount (INR)", min_value=0.0, value=25000.0, step=1000.0)
        
    with col2:
        st.markdown("### **Live Corporate Invoice Preview**")
        st.markdown(f"""
        <div style="background-color: white; padding: 2rem; border: 1px solid #E2E8F0; border-radius: 0.25rem;">
            <h3 style="color: #1E3A8A; margin-top: 0;">INVOICE</h3>
            <p><strong>Firm:</strong> Kulkarni Strategic Partners</p>
            <p><strong>Client:</strong> {client_name}</p>
            <hr style="border-top: 1px dashed #CBD5E1;">
            <p><strong>Description of Services:</strong><br>{service_desc}</p>
            <h4 style="text-align: right; margin-bottom: 0;">Total Due:</h4>
            <h2 style="text-align: right; color: #10B981; margin-top: 0;">₹{retainer_fee:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Finalize and Push Receipt Manifest to Ledger"):
            st.toast(f"Invoice logged for {client_name} - Retainer: ₹{retainer_fee:,.2f}", icon="💰")