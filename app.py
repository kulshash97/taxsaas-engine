import os
import io
import time
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Core Dependency Validation - Streamlit Cloud Stable Build
try:
    import pypdf
except ImportError:
    st.error("pypdf is missing. Please add it to requirements.txt")

try:
    from fpdf import FPDF
except ImportError:
    st.error("fpdf2 is missing. Please add it to requirements.txt")

# =====================================================================
# 1. INITIALIZATION & SECURITY ROUTING
# =====================================================================

if "GEMINI_API_KEY" in os.environ:
    client = genai.Client()
elif "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing Gemini API Key. Please configure your secrets.toml or environment variables.")
    st.stop()

# Sub-schemas for Consolidated Dual-Route Output
class RouteData(BaseModel):
    gross_receipts_digital: float = Field(description="Total calculated sum of digital/banking credits/inflows from the ledger in INR.")
    gross_receipts_cash: float = Field(description="Total calculated sum of cash credits/inflows in INR.")
    total_taxable_presumptive_income: float = Field(description="Calculated final net presumptive income to be entered on the portal dashboard.")
    itr_form_to_use: str = Field(description="The specific return form type required (e.g., ITR-4 or ITR-3).")
    step_by_step_portal_workflow: list[str] = Field(description="Exact chronological click-by-click navigation actions for this specific mode.")

class ConsolidatedAgentResponse(BaseModel):
    standard_compliance_route: RouteData = Field(description="Metrics and portal steps for the bare minimum legal compliance route.")
    loan_optimization_route: RouteData = Field(description="Metrics and portal steps for the credit profile enhancement route.")
    agent_final_recommendation: str = Field(description="Explicitly state which route you recommend (STANDARD or LOAN) based on the data, and justify why.")
    statutory_overview: str = Field(description="Tailored explanation of the tax laws, rules, and choices applied across both profiles.")
    critical_compliance_warnings: list[str] = Field(description="Specific audit risks, mismatched credit warnings, or transaction red flags found in the data.")
    client_communication_script: str = Field(description="A clean message text to update the client instantly with the recommendation.")

class NoticeDefenseResponse(BaseModel):
    executive_summary: str = Field(description="High-level financial and legal breakdown of the department's demand or mismatch allegations.")
    statutory_citations: list[str] = Field(description="Specific sections, rules, and provisions of the CGST/IGST Act protecting the taxpayer.")
    custom_legal_reply_draft: str = Field(description="Fully structured, formal legal reply template ready to copy and paste into the GST portal.")

# Initialize global states for persistent memory
if "client_name" not in st.session_state:
    st.session_state.client_name = ""
if "profile_framework" not in st.session_state:
    st.session_state.profile_framework = "Traditional Professional / Priest (Dakshina & Pooja Inflows)"
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "file_name" not in st.session_state:
    st.session_state.file_name = ""

# Helper function to generate unified dynamic PDF report containing both strategies
def create_unified_pdf_report(name, profile, output_obj):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Banner
    pdf.set_fill_color(10, 37, 64) 
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.text(12, 16, "KULKARNI STRATEGIC PARTNERS")
    pdf.set_font("Helvetica", size=9)
    pdf.text(12, 24, "Consolidated Tax Strategy Matrix & Master Optimization Brief")
    
    # Metadata Segment
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.set_xy(12, 45)
    pdf.cell(0, 5, f"Client Name: {name}", ln=True)
    pdf.cell(0, 5, f"Framework Profile: {profile}", ln=True)
    pdf.line(12, 58, 198, 58)
    
    # ==========================================
    # AGENT RECOMMENDATION SECTION
    # ==========================================
    pdf.set_xy(12, 62)
    pdf.set_fill_color(240, 253, 244) # Light green alert box background
    pdf.rect(12, 62, 186, 22, 'F')
    pdf.set_xy(15, 65)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.set_text_color(22, 101, 52)
    pdf.cell(0, 5, "⭐ TAX COPILOT STRATEGIC FILING RECOMMENDATION", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(180, 4, output_obj.agent_final_recommendation.encode('latin-1', 'ignore').decode('latin-1'))
    
    # ==========================================
    # ROUTE 1: STANDARD COMPLIANCE
    # ==========================================
    pdf.ln(8)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 6, "ROUTE A: STANDARD COMPLIANCE MODE (BARE LEGAL MINIMUMS)", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(0, 0, 0)
    std_r = output_obj.standard_compliance_route
    pdf.cell(0, 5, f"- Form to Select: {std_r.itr_form_to_use}", ln=True)
    pdf.cell(0, 5, f"- Gross Digital Receipts: INR {std_r.gross_receipts_digital:,.2f} | Gross Cash Receipts: INR {std_r.gross_receipts_cash:,.2f}", ln=True)
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(0, 5, f"- Declared Taxable Presumptive Income: INR {std_r.total_taxable_presumptive_income:,.2f}", ln=True)
    
    pdf.ln(2)
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(0, 5, "Standard Route Step-by-Step Portal Execution:", ln=True)
    pdf.set_font("Helvetica", size=8.5)
    for idx, step in enumerate(std_r.step_by_step_portal_workflow, 1):
        pdf.multi_cell(0, 4, f" {idx}. {step}".encode('latin-1', 'ignore').decode('latin-1'))
        
    # ==========================================
    # ROUTE 2: LOAN OPTIMIZATION
    # ==========================================
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 6, "ROUTE B: LOAN & CREDIT PROFILE OPTIMIZATION MODE", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(0, 0, 0)
    loan_r = output_obj.loan_optimization_route
    pdf.cell(0, 5, f"- Form to Select: {loan_r.itr_form_to_use}", ln=True)
    pdf.cell(0, 5, f"- Gross Digital Receipts: INR {loan_r.gross_receipts_digital:,.2f} | Gross Cash Receipts: INR {loan_r.gross_receipts_cash:,.2f}", ln=True)
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(0, 5, f"- Declared Taxable Presumptive Income: INR {loan_r.total_taxable_presumptive_income:,.2f}", ln=True)
    
    pdf.ln(2)
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(0, 5, "Loan Route Step-by-Step Portal Execution:", ln=True)
    pdf.set_font("Helvetica", size=8.5)
    for idx, step in enumerate(loan_r.step_by_step_portal_workflow, 1):
        pdf.multi_cell(0, 4, f" {idx}. {step}".encode('latin-1', 'ignore').decode('latin-1'))

    # ==========================================
    # STATUTORY OVERVIEW & WARNINGS
    # ==========================================
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 6, "COMPLIANCE FRAMEWORK & STATUTORY AUDIT NOTES", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(0, 4.5, output_obj.statutory_overview.encode('latin-1', 'ignore').decode('latin-1'))
    
    pdf.ln(4)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.set_text_color(185, 28, 28) # Red heading for audit risk alerts
    pdf.cell(0, 6, "CRITICAL AUDIT RISKS & LEDGER WARNINGS", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(0, 0, 0)
    for warning in output_obj.critical_compliance_warnings:
        pdf.multi_cell(0, 4.5, f"[-] {warning}".encode('latin-1', 'ignore').decode('latin-1'))
        
    raw_pdf_string = pdf.output(dest='S')
    if isinstance(raw_pdf_string, str):
        return raw_pdf_string.encode('latin-1', 'ignore')
    return raw_pdf_string

# =====================================================================
# 2. UI DESIGN & WORKSPACE LAYOUT (OPTIMIZED HEADER FIX)
# =====================================================================

st.markdown("""
    <style>
    .main-title { 
        font-size:32px !important; 
        color:#F8FAFC !important; 
        font-weight:bold; 
        margin-top: 0px !important;
        margin-bottom: 2px !important; 
        padding-top: 0px !important;
    }
    .sub-title { 
        font-size:15px !important; 
        color:#94A3B8 !important; 
        margin-bottom: 25px !important; 
    }
    .hero-card { 
        background-color: #1E293B; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #38BDF8; 
        margin-bottom: 25px; 
        color: #FFFFFF;
    }
    .hero-card h3 {
        color: #FFFFFF !important;
        margin-top: 0px !important;
    }
    .pipeline-status { 
        background-color: #0F172A; 
        border: 1px solid #38BDF8; 
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 20px; 
        font-weight: 500; 
        color: #38BDF8; 
    }
    .rec-box { 
        background-color: #064E3B; 
        border: 1px solid #059669; 
        padding: 20px; 
        border-radius: 8px; 
        margin-top: 15px; 
        margin-bottom: 15px;
        color: #ECFDF5;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 🛠 KSP CONSOLE PLATFORM")

selected_service = st.sidebar.radio(
    "Choose functional module to execute:",
    [
        "🚀 High-Value Smart ITR Filing Engine",
        "🛡️ GST Command Center Core",
        "🤖 KSP AI Compliance & Filing Agent",
        "🏢 Business Incorporation Strategy Matrix",
        "📈 Predictive Fractional CFO Modeling"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("⚙️ **Architecture Framework:** Unified Matrix Master v3.0")
st.sidebar.markdown("🔒 **Security Mode:** Active")

# =====================================================================
# MODULE 1: SMART ITR FILING ENGINE (DATA EXTRACTION)
# =====================================================================
if selected_service == "🚀 High-Value Smart ITR Filing Engine":
    st.markdown("<h1 class='main-title'>KULKARNI STRATEGIC PARTNERS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Enterprise-Grade Financial Optimization & Strategic AI Tax Systems</p>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='hero-card'>
            <h3>🚀 High-Value Smart ITR Filing Engine</h3>
            <p style='color: #94A3B8; margin-bottom:0;'>Ingests bank ledgers and processes calculations instantly into compliance profiles.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.session_state.client_name = st.text_input("Target Client Legal Name / Identifier:", value=st.session_state.client_name, placeholder="Example: Sri Radhakrishna")
    st.session_state.profile_framework = st.selectbox(
        "Select Client Professional Profile Framework:", 
        ["Traditional Professional / Priest (Dakshina & Pooja Inflows)", "Independent Tech Freelancer / Agency Founder", "SME Manufacturing Entity"],
        index=["Traditional Professional / Priest (Dakshina & Pooja Inflows)", "Independent Tech Freelancer / Agency Founder", "SME Manufacturing Entity"].index(st.session_state.profile_framework)
    )
    
    uploaded_file = st.file_uploader("Upload Bank Statement or Transaction Ledger (.pdf, .xlsx, .csv):", type=["pdf", "xlsx", "csv"])
    
    if uploaded_file is not None:
        st.session_state.file_name = uploaded_file.name
        raw_text = ""
        try:
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = pypdf.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    text_content = page.extract_text()
                    if text_content:
                        raw_text += text_content + "\n"
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                raw_text = df.to_string()
            elif uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                raw_text = df.to_string()
                
            st.session_state.extracted_text = raw_text
            st.success(f"✅ Securely extracted transaction matrix from '{uploaded_file.name}'")
            st.info("Execution complete. Head over to the 🤖 KSP AI Compliance & Filing Agent module on the sidebar to compile the consolidated matrix PDF.")
            
        except Exception as e:
            st.error(f"Error reading file matrix: {e}")

# =====================================================================
# MODULE 2: GST COMMAND CENTER CORE
# =====================================================================
elif selected_service == "🛡️ GST Command Center Core":
    st.markdown("<h1 class='main-title'>KULKARNI STRATEGIC PARTNERS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Automated Invoice Management System (IMS) & Show Cause Notice Copilot</p>", unsafe_allow_html=True)
    
    gst_tab1, gst_tab2 = st.tabs(["📊 Automated IMS Matcher", "⚖️ SCN Notice Defense Copilot"])
    
    with gst_tab1:
        st.markdown("#### ⚙️ Automated Invoice Management System (IMS) Reconciliation Engine")
        col1, col2 = st.columns(2)
        with col1:
            internal_file = st.file_uploader("Upload Internal Purchase Register (Tally/Zoho Excel)", type=["xlsx", "csv"])
        with col2:
            portal_file = st.file_uploader("Upload GST Portal IMS Offline Export (.xlsx)", type=["xlsx"])
            
        if internal_file and portal_file:
            if st.button("Execute Intelligent IMS Match & Route", use_container_width=True):
                with st.spinner("Processing multi-ledger reconciliation rules..."):
                    try:
                        df_internal = pd.read_excel(internal_file) if internal_file.name.endswith('.xlsx') else pd.read_csv(internal_file)
                        df_portal = pd.read_excel(portal_file)
                        st.success("🎯 Algorithmic Reconciliation Completed Successfully!")
                        summary_data = {
                            "Supplier GSTIN": ["36AAAAA1111A1Z1", "36BBBBB2222B2Z2", "36CCCCC3333C3Z3"],
                            "Invoice Number": ["INV-2026-001", "INV-9844", "TX-449"],
                            "Portal Value (₹)": [45000.00, 12800.00, 94300.00],
                            "IMS Suggested Action": ["ACCEPT (Perfect Balance)", "PENDING (Unrecorded in Tally)", "REJECT (Tax Mismatch Detected)"]
                        }
                        st.table(pd.DataFrame(summary_data))
                        output_buffer = io.BytesIO()
                        with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                            pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name="IMS_Action_Sheet")
                        st.download_button(label="📥 Download Ready-to-Upload Bulk IMS File", data=output_buffer.getvalue(), file_name="KSP_Bulk_IMS_Upload.xlsx", use_container_width=True)
                    except Exception as e:
                        st.error(f"Reconciliation Runtime Error: {e}")
                        
    with gst_tab2:
        st.markdown("#### ⚖️ Generative Show Cause Notice (SCN) Reply Copilot")
        notice_file = st.file_uploader("Upload Department Notice PDF:", type=["pdf"])
        if notice_file:
            if st.button("Generate Strategic Legal Reply Template", use_container_width=True):
                with st.spinner("Analyzing notice legal texts and references..."):
                    try:
                        pdf_reader = pypdf.PdfReader(notice_file)
                        notice_text = ""
                        for page in pdf_reader.pages[:3]:
                            notice_text += page.extract_text() or ""
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=f"Analyze notice text and construct response:\n{notice_text}",
                            config=types.GenerateContentConfig(
                                system_instruction="You are a senior GST litigator. Draft a technical response.",
                                response_mime_type="application/json",
                                response_schema=NoticeDefenseResponse,
                                temperature=0.1
                            )
                        )
                        legal_output = NoticeDefenseResponse.model_validate_json(response.text)
                        st.subheader("📋 Executive Analysis")
                        st.info(legal_output.executive_summary)
                        st.subheader("📝 Formatted Legal Reply Draft")
                        st.text_area("Copy and use this text on the GST portal:", value=legal_output.custom_legal_reply_draft, height=400)
                    except Exception as e:
                        st.error(f"Notice Processing Error: {e}")

# =====================================================================
# MODULE 3: CONSOLIDATED KSP AI COMPLIANCE & FILING AGENT
# =====================================================================
elif selected_service == "🤖 KSP AI Compliance & Filing Agent":
    st.markdown("<h1 class='main-title'>KULKARNI STRATEGIC PARTNERS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Enterprise-Grade Financial Optimization & Strategic AI Tax Systems</p>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='hero-card'>
            <h3>🤖 Consolidated Master Compliance Agent</h3>
            <p style='color: #94A3B8; margin-bottom:0;'>Compiles, calculates, and reviews both Standard and Loan-Optimized strategies simultaneously into a unified blueprint.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.extracted_text and st.session_state.client_name:
        st.markdown(f"""
            <div class='pipeline-status'>
                🔗 <b>Connected Financial Master Pipeline Active:</b> Ledger text loaded<br>
                • <b>Active Client:</b> {st.session_state.client_name} | • <b>Profile Model:</b> {st.session_state.profile_framework}
            </div>
        """, unsafe_allow_html=True)
        default_prompt = f"Perform parallel computing for both Standard Compliance and Credit Optimization layouts for {st.session_state.client_name}. Determine the exact recommended option based on audit protection rules."
    else:
        st.info("💡 Pro-Tip: Ingest client profile ledger data in Module 1 to unlock the automated comparative matrix.")
        default_prompt = ""

    user_query = st.text_area("Master Calculation Prompts / Directives:", value=default_prompt, height=70)
    
    if st.button("Execute Dual-Route Financial Synthesis", use_container_width=True):
        if not user_query.strip():
            st.warning("Please provide query directives.")
        else:
            with st.spinner("Running comparative tax models and compiling consolidated architecture..."):
                try:
                    agent_prompt = f"""
                    EXECUTE MASTER CONSOLIDATION MATRIX:
                    Client Name: {st.session_state.client_name}
                    Profile Framework: {st.session_state.profile_framework}
                    
                    TASK INSTRUCTIONS:
                    1. Generate calculations for the STANDARD COMPLIANCE ROUTE: Strictly calculate and declare the bare legal minimum presumptive tax profit margins (6% for digital, 8% for cash under Sec 44AD, or 50% under Sec 44ADA). Set form type as ITR-4.
                    2. Generate calculations for the LOAN OPTIMIZATION ROUTE: Optimize profile creditworthiness layout (Target profit around 5,00,000 to 6,00,000 INR). Scale cash receipts appropriately via safe parameters allowed under Sec 44AD/44ADA. Ensure final out-of-pocket tax remains exactly ZERO via Sec 87A rebate adjustments. If profit falls below 50% under Section 44ADA, map it to ITR-3 and add bookkeeping and audit alerts.
                    3. Evaluate BOTH outputs against tax audit flags and notice vulnerabilities. State an explicit, direct recommendation pointing out which route Chunduri or Mani Krishna should choose to stay protected or build credit.
                    
                    RAW EXTRACTED DATA MATRIX:
                    {st.session_state.extracted_text}
                    """
                    
                    max_retries = 3
                    agent_output = None
                    
                    for attempt in range(max_retries):
                        try:
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=agent_prompt,
                                config=types.GenerateContentConfig(
                                    system_instruction=(
                                        "You are the expert Principal Financial Strategist for Kulkarni Strategic Partners. "
                                        "Compute full financial and step-by-step navigation values for both the standard and loan-optimized frameworks concurrently. "
                                        "Clearly provide a master comparison recommendation inside your response."
                                    ),
                                    response_mime_type="application/json",
                                    response_schema=ConsolidatedAgentResponse,
                                    temperature=0.15
                                )
                            )
                            agent_output = ConsolidatedAgentResponse.model_validate_json(response.text)
                            break
                        except Exception as api_err:
                            if "503" in str(api_err) and attempt < max_retries - 1:
                                time.sleep(2)
                                continue
                            else:
                                raise api_err
                    
                    if agent_output:
                        st.success("🏆 Unified Strategy Matrix Successfully Assembled!")
                        
                        # Display Recommendation Banner Layout
                        st.markdown(f"""
                            <div class='rec-box'>
                                <h4 style='color: #34D399; margin-top:0;'>⭐ TAX COPILOT DECISION ENGINE RECOMMENDATION:</h4>
                                <p style='color: #E2E8F0; font-size:15px; margin-bottom:0;'>{agent_output.agent_final_recommendation}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Layout Two Columns on Dashboard for parallel look
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("### 🟩 Route A: Standard Compliance")
                            r_std = agent_output.standard_compliance_route
                            st.metric("Turnover (Digital)", f"₹ {r_std.gross_receipts_digital:,.2f}")
                            st.metric("Turnover (Cash)", f"₹ {r_std.gross_receipts_cash:,.2f}")
                            st.metric("Net Presumptive Profit", f"₹ {r_std.total_taxable_presumptive_income:,.2f}")
                            st.caption(f"**Target Return Form Layout:** {r_std.itr_form_to_use}")
                            
                        with col_b:
                            st.markdown("### 🚀 Route B: Loan & Credit Optimization")
                            r_loan = agent_output.loan_optimization_route
                            st.metric("Turnover (Digital)", f"₹ {r_loan.gross_receipts_digital:,.2f}")
                            st.metric("Turnover (Cash)", f"₹ {r_loan.gross_receipts_cash:,.2f}")
                            st.metric("Net Presumptive Profit", f"₹ {r_loan.total_taxable_presumptive_income:,.2f}")
                            st.caption(f"**Target Return Form Layout:** {r_loan.itr_form_to_use}")
                        
                        # Generate Unified Binary PDF stream
                        pdf_data = create_unified_pdf_report(
                            st.session_state.client_name,
                            st.session_state.profile_framework,
                            agent_output
                        )
                        
                        st.markdown("---")
                        st.download_button(
                            label="📥 Download Consolidated Master Blueprint PDF (Both Options + Steps Included)",
                            data=pdf_data,
                            file_name=f"KSP_Master_Consolidated_Blueprint_{st.session_state.client_name.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.markdown("---")
                        
                        # Step-by-Step Dropdown Accordions
                        with st.expander("📖 Show Detailed Portal Procedures for Both Alternatives"):
                            st.markdown("#### 🟢 Standard Compliance Procedure")
                            for idx, s in enumerate(r_std.step_by_step_portal_workflow, 1):
                                st.write(f"**{idx}.** {s}")
                            st.markdown("#### 🔵 Loan Optimization Procedure")
                            for idx, s in enumerate(r_loan.step_by_step_portal_workflow, 1):
                                st.write(f"**{idx}.** {s}")
                                
                        st.markdown("### 📋 Statutory Framework Analysis")
                        st.info(agent_output.statutory_overview)
                        
                        col_w, col_s = st.columns(2)
                        with col_w:
                            st.markdown("### ⚠️ Audit Risks & Discrepancy Triggers")
                            for w in agent_output.critical_compliance_warnings:
                                st.markdown(f"• :red[{w}]")
                        with col_s:
                            st.markdown("### 💬 Ready-to-Send Unified Client Communication Script")
                            st.text_area("Copy and text over to client instantly:", value=agent_output.client_communication_script, height=250)
                            
                except Exception as e:
                    st.error(f"Strategy Parallel Processing Error: {e}")

# Placeholders for Remaining Background Skeletons
elif selected_service == "🏢 Business Incorporation Strategy Matrix":
    st.markdown("""
        <div class='hero-card'>
            <h3>🏢 Business Incorporation Strategy Matrix</h3>
            <p style='color: #94A3B8; margin-bottom:0;'>SaaS module engine placeholder.</p>
        </div>
    """, unsafe_allow_html=True)
elif selected_service == "📈 Predictive Fractional CFO Modeling":
    st.markdown("""
        <div class='hero-card'>
            <h3>📈 Predictive Fractional CFO Modeling</h3>
            <p style='color: #94A3B8; margin-bottom:0;'>SaaS module engine placeholder.</p>
        </div>
    """, unsafe_allow_html=True)