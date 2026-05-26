import os
import io
import time
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Core Dependency Validation
try:
    import PyPDF2
except ImportError:
    st.error("PyPDF2 is missing. Please add it to requirements.txt")

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

# Structured Schemas for Multi-Agent Outputs
class ConnectedAgentResponse(BaseModel):
    detected_gross_receipts_digital: float = Field(description="Total calculated sum of digital/banking credits/inflows from the ledger in INR.")
    detected_gross_receipts_cash: float = Field(description="Total calculated sum of cash credits/inflows in INR.")
    total_taxable_presumptive_income: float = Field(description="Calculated final net presumptive income to be typed on the portal dashboard.")
    statutory_overview: str = Field(description="Tailored explanation of the tax laws, rules, and strategy choices applied.")
    step_by_step_portal_workflow: list[str] = Field(description="Exact chronological click-by-click navigation actions for the government portal.")
    critical_compliance_warnings: list[str] = Field(description="Specific audit risks, mismatched credit warnings, or transaction red flags found in the data.")
    client_communication_script: str = Field(description="A clean message text to update the client instantly.")

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

# Helper function to generate standard clean PDF documents dynamically
def create_pdf_report(name, profile, route, output_obj):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Banner
    pdf.set_fill_color(10, 37, 64) 
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.text(12, 18, "KULKARNI STRATEGIC PARTNERS")
    pdf.set_font("Helvetica", size=10)
    pdf.text(12, 26, "Automated Client Compliance Architecture & Filing Blueprint")
    
    # Metadata Segment
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.set_xy(12, 48)
    pdf.cell(0, 6, f"Client Name: {name}", ln=True)
    pdf.cell(0, 6, f"Framework Profile: {profile}", ln=True)
    pdf.cell(0, 6, f"Selected Strategy Route: {route.upper()}", ln=True)
    pdf.line(12, 70, 198, 70)
    
    # Calculated Figures Area
    pdf.set_xy(12, 75)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 8, "COMPUTED FINANCIAL SCHEDULING METRICS", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"- Aggregated Gross Digital Credits: INR {output_obj.detected_gross_receipts_digital:,.2f}", ln=True)
    pdf.cell(0, 6, f"- Aggregated Gross Cash Credits: INR {output_obj.detected_gross_receipts_cash:,.2f}", ln=True)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(0, 6, f"- Total Presumptive Net Income to Enter: INR {output_obj.total_taxable_presumptive_income:,.2f}", ln=True)
    
    # Statutory Segment
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 8, "STATUTORY OVERVIEW", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 5, output_obj.statutory_overview.encode('latin-1', 'ignore').decode('latin-1'))
    
    # Steps Segment
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 8, "PORTAL FILING MECHANICS CHECKLIST", ln=True)
    pdf.set_font("Helvetica", size=10)
    for idx, step in enumerate(output_obj.step_by_step_portal_workflow, 1):
        pdf.multi_cell(0, 5, f"Step {idx}: {step}".encode('latin-1', 'ignore').decode('latin-1'))
        
    # FIXED: Return pure binary string output format to avoid downstream casting bugs
    raw_pdf_string = pdf.output(dest='S')
    if isinstance(raw_pdf_string, str):
        return raw_pdf_string.encode('latin-1', 'ignore')
    return raw_pdf_string

# =====================================================================
# 2. UI DESIGN & WORKSPACE LAYOUT
# =====================================================================

st.set_page_config(page_title="KSP Cloud Workspace", page_icon="💼", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size:38px !important; color:#0A2540; font-weight:bold; margin-bottom: 5px; }
    .sub-title { font-size:16px !important; color:#4A607A; margin-bottom: 30px; }
    .hero-card { background-color: #F8FAFC; padding: 25px; border-radius: 12px; border-left: 6px solid #0A2540; margin-bottom: 25px; }
    .pipeline-status { background-color: #E0F2FE; border: 1px solid #7DD3FC; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: 500; color: #0369A1; }
    .metric-badge { background-color: #F0FDF4; border: 1px solid #BBF7D0; padding: 15px; border-radius: 8px; text-align: center; color: #166534; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 🛠 KSP CORE SERVICES COMMAND CONSOLE")

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
st.sidebar.markdown("⚙️ **Architecture Framework:** Unified Enterprise v2.0")
st.sidebar.markdown("🔒 **Security Mode:** Active")

# =====================================================================
# MODULE 1: SMART ITR FILING ENGINE (DATA EXTRACTION)
# =====================================================================
if selected_service == "🚀 High-Value Smart ITR Filing Engine":
    st.markdown("<div class='main-title'>💼 KULKARNI STRATEGIC PARTNERS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Enterprise-Grade Financial Optimization & Strategic AI Tax Systems</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-card'><h3>🚀 High-Value Smart ITR Filing Engine</h3><p>Ingests bank ledgers and processes calculations instantly into compliance profiles.</p></div>", unsafe_allow_html=True)
    
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
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
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
            st.info("Execution complete. Head over to the 🤖 KSP AI Compliance & Filing Agent module on the sidebar to trigger your strategy selections!")
            
        except Exception as e:
            st.error(f"Error reading file matrix: {e}")

# =====================================================================
# MODULE 2: GST COMMAND CENTER CORE (IMS RECONCILER & NOTICE DEFENSE)
# =====================================================================
elif selected_service == "🛡️ GST Command Center Core":
    st.markdown("<div class='main-title'>💼 KULKARNI STRATEGIC PARTNERS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Automated Invoice Management System (IMS) & Show Cause Notice Copilot</div>", unsafe_allow_html=True)
    
    gst_tab1, gst_tab2 = st.tabs(["📊 Automated IMS Matcher", "⚖️ SCN Notice Defense Copilot"])
    
    with gst_tab1:
        st.markdown("#### ⚙️ Automated Invoice Management System (IMS) Reconciliation Engine")
        st.write("Cross-references internal bookkeeping data with government portal files to execute bulk validation rules.")
        
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
                        
                        df_internal.columns = df_internal.columns.str.upper().str.strip()
                        df_portal.columns = df_portal.columns.str.upper().str.strip()
                        
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
                        
                        st.download_button(
                            label="📥 Download Ready-to-Upload Bulk IMS File",
                            data=output_buffer.getvalue(),
                            file_name="KSP_Bulk_IMS_Upload.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Reconciliation Runtime Error: {e}")
                        
    with gst_tab2:
        st.markdown("#### ⚖️ Generative Show Cause Notice (SCN) Reply Copilot")
        st.write("Upload any tax discrepancy notice or demand file (Form ASMT-10 / DRC-01) to auto-draft a structured legal reply template.")
        
        notice_file = st.file_uploader("Upload Department Notice PDF:", type=["pdf"])
        if notice_file:
            if st.button("Generate Strategic Legal Reply Template", use_container_width=True):
                with st.spinner("Analyzing notice legal texts and references..."):
                    try:
                        pdf_reader = PyPDF2.PdfReader(notice_file)
                        notice_text = ""
                        for page in pdf_reader.pages[:3]:
                            notice_text += page.extract_text() or ""
                            
                        notice_prompt = f"Analyze this GST department notice text and construct a defense draft:\n{notice_text}"
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=notice_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction="You are a senior GST litigator and tax expert. Draft a highly technical legal response contesting the allegations using strict statutory provisions.",
                                response_mime_type="application/json",
                                response_schema=NoticeDefenseResponse,
                                temperature=0.1
                            )
                        )
                        
                        legal_output = NoticeDefenseResponse.model_validate_json(response.text)
                        
                        st.subheader("📋 Executive Analysis")
                        st.info(legal_output.executive_summary)
                        
                        st.subheader("📚 Statutory Citations Leveraged")
                        for cit in legal_output.statutory_citations:
                            st.markdown(f"• **{cit}**")
                            
                        st.subheader("📝 Formatted Legal Reply Draft")
                        st.text_area("Copy and use this text on the GST portal:", value=legal_output.custom_legal_reply_draft, height=400)
                    except Exception as e:
                        st.error(f"Notice Processing Error: {e}")

# =====================================================================
# MODULE 5: CONNECTED KSP AI COMPLIANCE & FILING AGENT
# =====================================================================
elif selected_service == "🤖 KSP AI Compliance & Filing Agent":
    st.markdown("<div class='main-title'>💼 KULKARNI STRATEGIC PARTNERS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Enterprise-Grade Financial Optimization & Strategic AI Tax Systems</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-card'><h3>🤖 KSP AI Compliance & Portal Filing Agent</h3><p>Select optimization modes and export dynamic PDF preparation templates.</p></div>", unsafe_allow_html=True)
    
    if st.session_state.extracted_text and st.session_state.client_name:
        st.markdown(f"""
            <div class='pipeline-status'>
                🔗 <b>Connected Financial Pipeline Active:</b> Ledger content loaded<br>
                • <b>Active Client:</b> {st.session_state.client_name} | • <b>Profile Model:</b> {st.session_state.profile_framework}
            </div>
        """, unsafe_allow_html=True)
        
        selected_route = st.selectbox(
            "Select Portal Filing Strategy Mode:",
            [
                "Standard Compliance Mode (Declare Bare Legal Minimums)",
                "Loan & Credit Optimization Mode (Legally Maximize Profiles for Future Capital/Housing Loans)"
            ]
        )
        
        default_prompt = f"Perform data-driven tax routing calculations under the chosen '{selected_route}' layout for {st.session_state.client_name} using the provided transaction metrics."
    else:
        st.info("💡 Pro-Tip: Go to Module 1, fill in the fields, and upload a bank statement to pass data directly into this engine.")
        selected_route = "Standard Compliance Mode (Declare Bare Legal Minimums)"
        default_prompt = ""

    user_query = st.text_area("Filing Strategy System Context Prompts:", value=default_prompt, height=70)
    
    if st.button("Query KSP Strategy & Matrix Core", use_container_width=True):
        if not user_query.strip():
            st.warning("Please verify calculation context inputs.")
        else:
            with st.spinner("Compiling strategic financial models and executing calculations..."):
                try:
                    if "Loan & Credit Optimization Mode" in selected_route:
                        strategy_clause = """
                        STRATEGY MANDATE: LOAN & CREDIT PROFILE OPTIMIZATION MODE
                        - Do NOT restrict calculations to the bare minimum legal floors (6% / 8%).
                        - Legally maximize the declared net profit to match an optimal creditworthiness layout (e.g., Target Net Taxable Profit baseline around 5,10,000 to 6,00,000 INR).
                        - Scale cash receipts appropriately by safely accounting for potential un-deposited cash receipts or higher profit margin parameters explicitly permitted under Section 44AD/44ADA.
                        - Ensure final out-of-pocket tax calculation remains exactly ZERO after Section 87A New Tax Regime rebates.
                        """
                    else:
                        strategy_clause = """
                        STRATEGY MANDATE: STANDARD COMPLIANCE MODE
                        - Strictly calculate and declare the bare legal minimum presumptive tax profit margins (6% for digital receipts, 8% for cash receipts under Section 44AD, or 50% under Section 44ADA).
                        - Reflect data strictly limited to the provided ledger credit amounts.
                        """
                    
                    agent_prompt = f"""
                    CONTEXT ENVIRONMENT ARCHITECTURE:
                    Client Name: {st.session_state.client_name}
                    Profile Framework: {st.session_state.profile_framework}
                    Chosen Filing Route: {selected_route}
                    
                    {strategy_clause}
                    
                    RAW EXTRACTED BANK LEDGER TEXT DATA:
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
                                        "You are the advanced strategic financial advisor AI for KSP. "
                                        "Your job is to read bank statement strings and strictly adapt your numbers based on the strategy chosen. "
                                        "If standard mode is selected, output the minimum rates. If loan mode is selected, output optimized credit entries "
                                        "and justify the high credit profit margin logically while maintaining zero out-of-pocket tax."
                                    ),
                                    response_mime_type="application/json",
                                    response_schema=ConnectedAgentResponse,
                                    temperature=0.15
                                )
                            )
                            agent_output = ConnectedAgentResponse.model_validate_json(response.text)
                            break
                        except Exception as api_err:
                            if "503" in str(api_err) and attempt < max_retries - 1:
                                time.sleep(2)
                                continue
                            else:
                                raise api_err
                    
                    if agent_output:
                        st.success(f"✅ Blueprint Compiled Under: {selected_route}")
                        
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown(f"<div class='metric-badge'><b>Gross Digital Credits</b><br><h3>₹ {agent_output.detected_gross_receipts_digital:,.2f}</h3></div>", unsafe_allow_html=True)
                        with m2:
                            st.markdown(f"<div class='metric-badge'><b>Gross Cash Credits</b><br><h3>₹ {agent_output.detected_gross_receipts_cash:,.2f}</h3></div>", unsafe_allow_html=True)
                        with m3:
                            st.markdown(f"<div class='metric-badge'><b>Total Net Entry Profit</b><br><h3>₹ {agent_output.total_taxable_presumptive_income:,.2f}</h3></div>", unsafe_allow_html=True)
                        
                        pdf_data = create_pdf_report(
                            st.session_state.client_name, 
                            st.session_state.profile_framework, 
                            selected_route, 
                            agent_output
                        )
                        
                        st.markdown("---")
                        # FIXED: Passed pdf_data directly as safe byte output string
                        st.download_button(
                            label="📥 Download This Filing Blueprint PDF",
                            data=pdf_data,
                            file_name=f"KSP_Filing_Blueprint_{st.session_state.client_name.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.markdown("---")
                        
                        st.markdown("### 📋 Statutory Overview")
                        st.info(agent_output.statutory_overview)
                        
                        st.markdown("### ⚙️ Step-by-Step Portal Filing Mechanics")
                        for index, step in enumerate(agent_output.step_by_step_portal_workflow, 1):
                            st.markdown(f"**Step {index}:** {step}")
                            
                        col_warn, col_script = st.columns(2)
                        with col_warn:
                            st.markdown("### ⚠️ Critical Audit Risks & Ledger Warnings")
                            for warning in agent_output.critical_compliance_warnings:
                                st.markdown(f"• :red[{warning}]")
                        with col_script:
                            st.markdown("### 💬 Ready-to-Send Client Message Script")
                            st.text_area("Copy text template directly:", value=agent_output.client_communication_script, height=350)
                            
                except Exception as e:
                    st.error(f"Strategy Compilation Routing Error: {e}")

# Placeholders for Remaining Background Skeletons
elif selected_service == "🏢 Business Incorporation Strategy Matrix":
    st.markdown("<div class='hero-card'><h3>🏢 Business Incorporation Strategy Matrix</h3><p>SaaS module engine placeholder.</p></div>", unsafe_allow_html=True)
elif selected_service == "📈 Predictive Fractional CFO Modeling":
    st.markdown("<div class='hero-card'><h3>📈 Predictive Fractional CFO Modeling</h3><p>SaaS module engine placeholder.</p></div>", unsafe_allow_html=True)