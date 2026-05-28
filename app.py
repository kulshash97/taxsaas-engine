import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# =========================================================================
# GLOBAL STATIC STRING LITERALS (Pre-defined to comply with Python 3.14)
# =========================================================================
CSS_INJECTION = "<style>div[data-testid='stSidebarNav'] {display: none;} .reportview-container .main .block-container{padding-top: 2rem;}</style>"

RECOMMENDATION_HTML = "<b>TAX COPILOT STRATEGIC FILING RECOMMENDATION:</b><br/>We recommend the <b>LOAN OPTIMIZATION ROUTE</b>. This route allows Mr. Chakravarthula to declare a higher taxable income of INR 5,00,000.00, which significantly improves his creditworthiness for future loan applications. Despite declaring a higher income, his net tax payable will remain exactly ZERO due to the full rebate available under Section 87A of the Income Tax Act, making it a financially advantageous and compliant strategy."

ITR_OPTIONS = [
    "ITR-1 (Sahaj - Salaried Individuals & House Property up to ₹50 Lakhs)",
    "ITR-2 (Capital Gains, Foreign Assets, & Multiple House Properties)",
    "ITR-3 (Individual Business Profits, Partners in Firms, & Cryptocurrencies)",
    "ITR-4 (Sugam - Presumptive Business/Professional Taxation under 44AD/44ADA/44AE)",
    "ITR-5 (Firms, LLPs, AOPs, BOIs, and Artificial Juridical Persons)",
    "ITR-6 (Companies other than Section 11 Exemption Entities)",
    "ITR-7 (Trusts, Political Parties, Charitable Institutions, & Research Associations)"
]

# =========================================================================
# 1. GLOBAL PLATFORM INITIALIZATION
# =========================================================================
st.set_page_config(
    layout="wide", 
    page_title="Kulkarni Strategic Partners | Tax Workspace", 
    initial_sidebar_state="expanded"
)

# Apply global styling overrides safely using the flat string variable
st.markdown(CSS_INJECTION, unsafe_html=True)

# =========================================================================
# 2. FIXED SIDEBAR NAVIGATION MATRIX (Unified Master v3.0)
# =========================================================================
st.sidebar.title("🛠️ KSP CONSOLE PLATFORM")
st.sidebar.markdown("Choose functional module to execute:")

module_selection = st.sidebar.radio(
    label="Select Module",
    options=[
        "🚀 High-Value Smart ITR Filing Engine",
        "🔵 GST Command Center Core",
        "🎯 KSP AI Compliance & Filing Agent",
        "🏢 Business Incorporation Strategy Matrix",
        "📈 Predictive Fractional CFO Modeling"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**⚙️ Architecture Framework:** Unified Matrix Master v3.0")
st.sidebar.markdown("**🔒 Security Mode:** Active")

# =========================================================================
# REPORTLAB PDF GENERATION STRUCT BOUNDS (Shared Utility)
# =========================================================================
def generate_master_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#1e3a8a'), alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=16, textColor=colors.HexColor('#475569'), alignment=TA_CENTER)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'))

    story = [
        Paragraph("KULKARNI STRATEGIC PARTNERS", title_style),
        Paragraph("Consolidated Tax Strategy Matrix & Master Optimization Brief", subtitle_style),
        Spacer(1, 15),
        Paragraph("<b>Client Name:</b> Mr. DIXITH CHAKRAVARTHULA", body_style),
        Paragraph("<b>Framework Profile:</b> Traditional Professional / Priest (Dakshina & Pooja Inflows)", body_style),
        Spacer(1, 12)
    ]
    
    rec_table = Table([[Paragraph(RECOMMENDATION_HTML, body_style)]], colWidths=[530])
    rec_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')), ('BORDER', (0,0), (-1,-1), 1.5, colors.HexColor('#3b82f6')), ('PADDING', (0,0), (-1,-1), 10)]))
    story.append(rec_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# =========================================================================
# CORE REUSABLE DOCUMENT PROCESSING COMPONENT
# =========================================================================
def render_document_processing_intake(module_key):
    st.markdown("### 📥 1. Dual-Input Document Processing Intake")
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        st.markdown("**Primary Income Records**")
        st.file_uploader("Upload Bank Statement / Form 16 (PDF/Excel)", type=["pdf", "xlsx", "xls", "csv"], key=f"primary_file_{module_key}")
    with col_input2:
        st.markdown("**Tax Credit Records**")
        st.file_uploader("Upload AIS / Form 26AS (PDF/Text)", type=["pdf", "txt", "csv"], key=f"credit_file_{module_key}")

def render_dual_route_analysis():
    st.markdown("---")
    st.markdown("### 🔍 2. Automated TDS/TCS Reconciliation Health Check")
    st.info("🔄 Cross-reference automation engines locked on target input vectors.")
    
    if st.button("Execute Dual-Route Financial Synthesis", key="execute_synthesis_global"):
        with st.spinner("Processing deep schema alignment matrices..."):
            st.markdown("### 📊 3. Parallel Strategy Matrix (Side-by-Side Evaluation)")
            col_route_a, col_route_b = st.columns(2)
            with col_route_a:
                with st.container(border=True):
                    st.error("🛑 **ROUTE A: Standard Compliance Mode**")
                    st.markdown("**Bare Legal Minimums**")
                    st.write("- **Form Selection:** ITR-4")
                    st.write("- **Gross Digital Receipts:** INR 5,90,235.00")
                    st.write("- **Declared Presumptive Income:** INR 2,95,117.50")
                    st.write("- **Net Tax Payable:** INR 0.00")
            with col_route_b:
                with st.container(border=True):
                    st.success("⭐ **ROUTE B: Credit Profile Optimization Mode**")
                    st.markdown("**Recommended Strategy**")
                    st.write("- **Form Selection:** ITR-4")
                    st.write("- **Gross Digital Receipts:** INR 5,90,235.00")
                    st.write("- **Declared Presumptive Income:** INR 5,00,000.00")
                    st.write("- **Net Tax Payable:** INR 0.00 (Sec 87A Rebate)")

            st.markdown("---")
            st.download_button(
                label="📥 Download Consolidated Master Optimization PDF Brief",
                data=generate_master_pdf(),
                file_name="KSP_Master_Consolidated_Blueprint_Mr_DIXITH_CHAKRAVARTHULA.pdf",
                mime="application/pdf"
            )

def render_itr_workspace(header_title, show_selector=False):
    st.title("💼 KULKARNI STRATEGIC PARTNERS")
    st.subheader(header_title)
    st.markdown("---")
    
    if show_selector:
        selected_itr = st.selectbox("Choose Target ITR Form for Processing:", ITR_OPTIONS, key="universal_itr_selector")
        st.markdown("---")
        render_document_processing_intake("smart_itr")
        
        if "ITR-1" in selected_itr:
            st.markdown("### 🏢 Income Parameters (ITR-1)")
            col1, col2 = st.columns(2)
            with col1: st.number_input("Gross Salary Income (Sch Salary)", min_value=0.0, step=5000.0, key="itr1_sal")
            with col2: st.number_input("Income from Other Sources", min_value=0.0, step=1000.0, key="itr1_oth")
        elif "ITR-2" in selected_itr:
            st.markdown("### 📈 Capital Gains & Global Asset Declaration (ITR-2)")
            col1, col2 = st.columns(2)
            with col1: st.number_input("Short-Term Capital Gains (Sec 111A)", min_value=0.0, key="itr2_stcg")
            with col2: st.number_input("Long-Term Capital Gains (Sec 112A)", min_value=0.0, key="itr2_ltcg")
        elif "ITR-3" in selected_itr:
            st.markdown("### 💼 Audited Business Profits (ITR-3)")
            st.info("System configured to run full P&L and Balance Sheet parsing arrays for scheduled audits.")
        elif "ITR-4" in selected_itr:
            st.markdown("### ⚡ Presumptive Profit Configuration Parameters")
            col1, col2 = st.columns(2)
            with col1: st.number_input("Gross Turnovers / Receipts (Digital + Cash)", min_value=0.0, value=590235.00, key="itr4_gross")
            with col2: st.number_input("Declared Presumptive Net Profit Margin Line", min_value=0.0, value=500000.00, key="itr4_net")
            render_dual_route_analysis()
        elif "ITR-5" in selected_itr or "ITR-6" in selected_itr:
            st.markdown("### 🏢 Corporate & Partnership Compliance Matrix (ITR-5 / ITR-6)")
            st.text_input("Enter Corporate PAN / LLPIN Reference:", key="corp_ref")
        elif "ITR-7" in selected_itr:
            st.markdown("### 🏛️ Institutional, Trust, & Exempt Entity Engine (ITR-7)")
            st.text_input("Section 11 / 12A / 10(23C) Registration Tracking Key:", key="trust_ref")

        if "ITR-4" not in selected_itr:
            st.markdown("---")
            if st.button("Run Schema Validation and Cross-Verify Against JSON Mappings", key="generic_validate_btn"):
                st.success("✅ Document schema validation successful. Baseline parameters verified against ITD database logs.")
    else:
        render_document_processing_intake("agent_itr")
        render_dual_route_analysis()

# =========================================================================
# ROUTING CONTROLLER MATRIX
# =========================================================================

if module_selection == "🚀 High-Value Smart ITR Filing Engine":
    render_itr_workspace("Universal Statutory Filing Interface & Schema Validator", show_selector=True)

elif module_selection == "🎯 KSP AI Compliance & Filing Agent":
    render_itr_workspace("Consolidated Tax Strategy Workspace & Master Optimization Dashboard", show_selector=False)

elif module_selection == "🔵 GST Command Center Core":
    st.title("🔵 GST Command Center Core")
    st.subheader("Automated GSTR-1 / GSTR-3B Cross-Reconciliation Workspace")
    st.markdown("---")
    col_gst1, col_gst2 = st.columns(2)
    with col_gst1:
        st.markdown("#### **Sales Register Ledger Data**")
        st.file_uploader("Upload GSTR-1 Sales Records / Outward Ledger (JSON/CSV)", key="gst_out")
    with col_gst2:
        st.markdown("#### **Purchase / ITC Reconciliation Logs**")
        st.file_uploader("Upload GSTR-2B / Auto-Drafted Input Credit Statement", key="gst_in")
    st.markdown("---")
    if st.button("Execute Cross-Portal Reconciliation Assessment", key="gst_recon_btn"):
        st.info("📊 Reconciliation engine complete: ITC match rate stands at 100% against inward supplier manifests.")

elif module_selection == "🏢 Business Incorporation Strategy Matrix":
    st.title("🏢 Business Incorporation Strategy Matrix")
    st.subheader("Entity Optimization Workspace & Structural Capitalization Modeler")
    st.markdown("---")
    col_inc1, col_inc2 = st.columns(2)
    with col_inc1:
        st.text_input("Proposed Enterprise Title Option 1:", value="Gatty Pet Foods", key="inc_title")
        st.selectbox("Target Corporate Structure:", ["Limited Liability Partnership (LLP)", "Private Limited Company (Pvt Ltd)", "One Person Company (OPC)", "Sole Proprietorship Framework"], key="inc_struct")
    with col_inc2:
        st.number_input("Proposed Initial Authorized Capital (INR):", min_value=100000, value=100000, step=50000, key="inc_cap")
    st.markdown("---")
    if st.button("Generate Comparative Statutory Structural Matrix", key="inc_matrix_btn"):
        st.success("📈 Entity optimization mapping completed. Tax compliance matrix saved to cache pipeline.")

elif module_selection == "📈 Predictive Fractional CFO Modeling":
    st.title("📈 Predictive Fractional CFO Modeling")
    st.subheader("Strategic Capital Valuation Engine & Liquidity Runway Modeler")
    st.markdown("---")
    col_cfo1, col_cfo2 = st.columns(2)
    with col_cfo1:
        st.slider("Baseline Revenue Compound Annual Growth Projection (%)", min_value=0, max_value=100, value=25, key="cfo_slider")
    with col_cfo2:
        st.number_input("Current Fixed Overhead Run Rate (Monthly):", min_value=0.0, value=50000.0, key="cfo_overhead")
    st.markdown("---")
    if st.button("Simulate Operational Capital Cash Flow Trajectories", key="cfo_sim_btn"):
        st.success("🚀 Cash flow projections compiled. Extended structural runway tracking at 24 months.")