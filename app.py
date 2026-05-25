import os
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Ensure PyPDF2 is imported to read PDF statements smoothly
try:
    import PyPDF2
except ImportError:
    st.error("PyPDF2 is missing. Please ensure it's listed in your requirements.txt")

# =====================================================================
# 1. INITIALIZATION & SECURITY ROUTING
# =====================================================================

if "GEMINI_API_KEY" in os.environ:
    client = genai.Client()
elif "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing Gemini API Key. Please configure your secrets.toml file.")
    st.stop()

# Expanded Schema to capture the exact mathematical and ledger breakdown
class ConnectedAgentResponse(BaseModel):
    detected_gross_receipts_digital: float = Field(description="Total calculated sum of digital/banking credits/inflows from the ledger in INR.")
    detected_gross_receipts_cash: float = Field(description="Total calculated or estimated sum of cash credits/inflows in INR.")
    presumptive_income_digital_6pct: float = Field(description="Calculated presumptive income under Sec 44AD/44ADA for digital receipts (6% or 50% depending on section).")
    presumptive_income_cash_8pct: float = Field(description="Calculated presumptive income under Sec 44AD for cash receipts (8%).")
    total_taxable_presumptive_income: float = Field(description="Sum of digital and cash presumptive incomes.")
    statutory_overview: str = Field(description="Tailored explanation of the tax laws, sections, and formulas applied.")
    step_by_step_portal_workflow: list[str] = Field(description="Exact chronological click-by-click navigation actions for the tax portal.")
    critical_compliance_warnings: list[str] = Field(description="Specific audit risks, mismatched credit warnings, or transaction red flags found in the bank data.")
    client_communication_script: str = Field(description="A clean message script containing the calculated figures to update the client.")

# =====================================================================
# 2. UI DESIGN & SIDEBAR WORKSPACE NAVIGATION
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

st.sidebar.markdown("## 🛠️ CORE SERVICES COMMAND CONSOLE")

selected_service = st.sidebar.radio(
    "Choose functional module to execute:",
    [
        "🚀 High-Value Smart ITR Filing Engine",
        "🏢 Business Incorporation Strategy Matrix",
        "🛡️ GST Section 17(5) Credit Auditor",
        "📈 Predictive Fractional CFO Modeling",
        "🤖 KSP AI Compliance & Filing Agent"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("⚙️ **Architecture Framework:** Mathematical Pipeline v6.0")
st.sidebar.markdown("🔒 **Security Mode:** Active")

# Initialize global states for cross-module variables
if "client_name" not in st.session_state:
    st.session_state.client_name = ""
if "profile_framework" not in st.session_state:
    st.session_state.profile_framework = "Traditional Professional / Priest (Dakshina & Pooja Inflows)"
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "file_name" not in st.session_state:
    st.session_state.file_name = ""

# =====================================================================
# MODULE 1: SMART ITR FILING ENGINE (DATA EXTRACTION LAYER)
# =====================================================================
if selected_service == "🚀 High-Value Smart ITR Filing Engine":
    st.markdown("<div class='main-title'>💼 KULKARNI STRATEGIC PARTNERS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Enterprise-Grade Financial Optimization & Strategic AI Tax Systems</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-card'><h3>🚀 High-Value Smart ITR Filing Engine</h3><p>Ingests bank ledgers and processes calculations instantly into compliance profiles.</p></div>", unsafe_allow_html=True)
    
    st.session_state.client_name = st.text_input("Target Client Legal Name / Identifier:", value=st.session_state.client_name, placeholder="Example: Sri Radhakrishna")
    
    st.session_state.profile_framework = st.selectbox(
        "Select Client Professional Profile Framework:", 
        [
            "Traditional Professional / Priest (Dakshina & Pooja Inflows)", 
            "Independent Tech Freelancer / Agency Founder", 
            "SME Manufacturing Entity"
        ],
        index=["Traditional Professional / Priest (Dakshina & Pooja Inflows)", "Independent Tech Freelancer / Agency Founder", "SME Manufacturing Entity"].index(st.session_state.profile_framework)
    )
    
    uploaded_file = st.file_uploader("Upload Bank Statement or Transaction Ledger (.pdf, .xlsx, .csv):", type=["pdf", "xlsx", "csv"])
    
    if uploaded_file is not None:
        st.session_state.file_name = uploaded_file.name
        raw_text = ""
        
        try:
            # Route 1: Handle PDF statements
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    text_content = page.extract_text()
                    if text_content:
                        raw_text += text_content + "\n"
            
            # Route 2: Handle Excel sheets
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                raw_text = df.to_string()
                
            # Route 3: Handle CSV sheets
            elif uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                raw_text = df.to_string()
                
            st.session_state.extracted_text = raw_text
            st.success(f"✅ Securely extracted transaction matrix from '{uploaded_file.name}'")
            
            if st.button("⚡ Trigger Connected Mathematical Routing & Generate Filing Guide"):
                st.switch_page("app.py")
                
        except Exception as e:
            st.error(f"Error reading file matrix: {e}")

# Placeholders for Modules 2, 3, 4
elif selected_service == "🏢 Business Incorporation Strategy Matrix":
    st.markdown("<div class='hero-card'><h3>🏢 Business Incorporation Strategy Matrix</h3></div>", unsafe_allow_html=True)
elif selected_service == "🛡️ GST Section 17(5) Credit Auditor":
    st.markdown("<div class='hero-card'><h3>🛡️ GST Section 17(5) Credit Auditor</h3></div>", unsafe_allow_html=True)
elif selected_service == "📈 Predictive Fractional CFO Modeling":
    st.markdown("<div class='hero-card'><h3>📈 Predictive Fractional CFO Modeling</h3></div>", unsafe_allow_html=True)

# =====================================================================
# MODULE 5: CONNECTED KSP AI COMPLIANCE & FILING AGENT (MATHEMATICAL CORE)
# =====================================================================
elif selected_service == "🤖 KSP AI Compliance & Filing Agent":
    st.markdown("<div class='main-title'>💼 KULKARNI STRATEGIC PARTNERS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Enterprise-Grade Financial Optimization & Strategic AI Tax Systems</div>", unsafe_allow_html=True)
    
    if st.session_state.extracted_text and st.session_state.client_name:
        st.markdown(f"""
            <div class='pipeline-status'>
                🔗 <b>Connected Financial Pipeline Active:</b> Ledger content loaded<br>
                • <b>Client Name:</b> {st.session_state.client_name}<br>
                • <b>Target Profile:</b> {st.session_state.profile_framework}<br>
                • <b>Active Processing File:</b> {st.session_state.file_name}
            </div>
        """, unsafe_allow_html=True)
        
        default_prompt = f"Perform complete statutory mathematical calculations and provide a step-by-step e-filing portal setup guide for {st.session_state.client_name} based on the extracted transaction history data provided below."
    else:
        st.info("💡 Pro-Tip: Go to Module 1, fill in the fields, and upload a bank statement to pass transaction logic directly into this mathematical compiler.")
        default_prompt = ""

    user_query = st.text_area("Filing Matrix Context Core Instructions:", value=default_prompt, height=100)
    
    if st.button("Query KSP Computational Core", use_container_width=True):
        if not user_query.strip():
            st.warning("Please verify the instructions query text.")
        else:
            with st.spinner("Processing deep math analysis on the transaction ledger logs..."):
                try:
                    # Packaging the prompt along with the exact textual ledger metrics extracted from the statement
                    agent_prompt = f"""
                    CONTEXT ENVIRONMENT ARCHITECTURE:
                    Client Name: {st.session_state.client_name}
                    Profile Framework: {st.session_state.profile_framework}
                    
                    RAW EXTRACTED BANK LEDGER TEXT DATA:
                    ---START OF LEDGER---
                    {st.session_state.extracted_text}
                    ---END OF LEDGER---
                    
                    GOAL:
                    1. Read the transaction entries, locate deposits/credits.
                    2. Calculate the total digital/banking receipts vs cash receipts.
                    3. Calculate the correct presumptive profit under the relevant section (Section 44AD: 6% for digital, 8% for cash. Section 44ADA: 50% for freelancers).
                    4. Output the final financial variables alongside click-by-click portal submission mechanics.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=agent_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are the specialized math-driven KSP AI Compliance Agent. "
                                "Your core strength is processing text-based financial data, aggregating total values accurately, "
                                "running tax percentage calculations (6%, 8%, or 50% profit rules), and formulating clear portal steps."
                            ),
                            response_mime_type="application/json",
                            response_schema=ConnectedAgentResponse,
                            temperature=0.1
                        )
                    )
                    
                    agent_output = ConnectedAgentResponse.model_validate_json(response.text)
                    st.success("✅ Computational Analysis & Tax Layout Successfully Compiled!")
                    
                    # Layout calculated values prominently using a row layout
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f"<div class='metric-badge'><b>Gross Digital Credits</b><br><h3>₹ {agent_output.detected_gross_receipts_digital:,.2f}</h3></div>", unsafe_allow_html=True)
                    with m2:
                        st.markdown(f"<div class='metric-badge'><b>Gross Cash Credits</b><br><h3>₹ {agent_output.detected_gross_receipts_cash:,.2f}</h3></div>", unsafe_allow_html=True)
                    with m3:
                        st.markdown(f"<div class='metric-badge'><b>Total Taxable Income</b><br><h3>₹ {agent_output.total_taxable_presumptive_income:,.2f}</h3></div>", unsafe_allow_html=True)
                        
                    st.markdown("---")
                    
                    # Display statutory breakdowns and step instructions
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
                        st.text_area("Copy and paste to update your client instantly:", value=agent_output.client_communication_script, height=350)
                        
                except Exception as e:
                    st.error(f"Computational Routing Error: {e}")