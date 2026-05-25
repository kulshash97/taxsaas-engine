import os
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

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

# Initialize global session memory states for pipeline connectivity
if "client_name" not in st.session_state:
    st.session_state.client_name = ""
if "profile_framework" not in st.session_state:
    st.session_state.profile_framework = "Traditional Professional / Priest (Dakshina & Pooja Inflows)"
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# Structured Schema for the Connected AI Compliance Agent
class ConnectedAgentResponse(BaseModel):
    statutory_overview: str = Field(description="Tailored explanation of the tax laws, rules, and sections specifically applicable to this client profile and income source.")
    step_by_step_portal_workflow: list[str] = Field(description="Exact, chronological click-by-click navigation actions to execute on the government portal based on the profile context.")
    critical_compliance_warnings: list[str] = Field(description="Specific audit risks, penalties, and common entry mistakes to avoid for this client scenario.")
    client_communication_script: str = Field(description="A ready-to-use message text to copy-paste to the client summarizing the action taken and next steps.")

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
st.sidebar.markdown("⚙️ **Architecture Framework:** Connected Pipeline v5.0")
st.sidebar.markdown("🔒 **Security Mode:** Active")

# =====================================================================
# MODULE 1: SMART ITR FILING ENGINE (DATA CAPTURE LAYER)
# =====================================================================
if selected_service == "🚀 High-Value Smart ITR Filing Engine":
    st.markdown("<div class='main-title'>💼 KULKARNI STRATEGIC PARTNERS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Enterprise-Grade Financial Optimization & Strategic AI Tax Systems</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-card'><h3>🚀 High-Value Smart ITR Filing Engine</h3><p>Ingests statement metrics live into encrypted institutional report formats.</p></div>", unsafe_allow_html=True)
    
    # Capture variables and bind directly to global session states
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
    
    uploaded_file = st.file_uploader("Upload Bank Statement, Transaction Ledger (.pdf, .xlsx, .csv):")
    
    if uploaded_file is not None:
        st.session_state.file_uploaded = True
        st.success(f"✅ Securely staged data file: '{uploaded_file.name}' for {st.session_state.client_name if st.session_state.client_name else 'Client'}")
        
        # Shortcut button to jump straight into the AI agent processing pipeline
        if st.button("⚡ Trigger Connected AI Compliance Router & Generate Filing Guide"):
            st.switch_page("app.py") # Triggers refresh with data locked in memory

# =====================================================================
# MODULE 2, 3, 4: OTHER CORE SERVICES (PLACEHOLDERS)
# =====================================================================
elif selected_service == "🏢 Business Incorporation Strategy Matrix":
    st.markdown("<div class='hero-card'><h3>🏢 Business Incorporation Strategy Matrix</h3><p>Evaluates corporate tax optimization models across regular LLP vs Private Limited structures.</p></div>", unsafe_allow_html=True)

elif selected_service == "🛡️ GST Section 17(5) Credit Auditor":
    st.markdown("<div class='hero-card'><h3>🛡️ GST Section 17(5) Credit Auditor</h3><p>Scans purchasing books against blocked input tax credit parameters to prevent leakage.</p></div>", unsafe_allow_html=True)

elif selected_service == "📈 Predictive Fractional CFO Modeling":
    st.markdown("<div class='hero-card'><h3>📈 Predictive Fractional CFO Modeling</h3><p>Generates multi-year forward financial projections and capital layout strategies.</p></div>", unsafe_allow_html=True)

# =====================================================================
# MODULE 5: CONNECTED KSP AI COMPLIANCE & FILING AGENT (INTELLIGENCE CORE)
# =====================================================================
elif selected_service == "🤖 KSP AI Compliance & Filing Agent":
    st.markdown("<div class='main-title'>💼 KULKARNI STRATEGIC PARTNERS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Enterprise-Grade Financial Optimization & Strategic AI Tax Systems</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-card'><h3>🤖 KSP AI Compliance & Portal Filing Agent</h3><p>Enterprise-grade white-label regulatory research agent with cross-module connection capabilities.</p></div>", unsafe_allow_html=True)
    
    # PIPELINE INTEGRATION STATUS BOX
    # Automatically senses if data exists from Module 1 and cross-injects it
    if st.session_state.file_uploaded and st.session_state.client_name:
        st.markdown(f"""
            <div class='pipeline-status'>
                🔗 <b>Connected Pipeline Active:</b> Auto-detecting context from Module 1<br>
                • <b>Client Name:</b> {st.session_state.client_name}<br>
                • <b>Profile Type:</b> {st.session_state.profile_framework}
            </div>
        """, unsafe_allow_html=True)
        
        # Construct an auto-prompt using the captured variables
        default_prompt = f"Provide a complete, step-by-step portal filing workflow guide for my client {st.session_state.client_name} who operates under the framework profile: {st.session_state.profile_framework}. A bank statement has been staged."
    else:
        st.info("💡 Pro-Tip: You can query manually below, or upload a bank statement in 'Module 1' to pass client data into this agent automatically.")
        default_prompt = ""

    user_query = st.text_area(
        "Filing Bottleneck or Context Instruction Core:",
        value=default_prompt,
        placeholder="Type custom dilemma or let the automated module pipeline fill this out...",
        height=120
    )
    
    if st.button("Query KSP Intelligence Core", use_container_width=True):
        if not user_query.strip():
            st.warning("Please enter or verify the compliance query context.")
        else:
            with st.spinner("Analyzing active Income Tax, GST, and MCA statutes based on cross-module client data..."):
                try:
                    agent_prompt = f"""
                    CONTEXT ENVIRONMENT DATA:
                    Client Identity Name: {st.session_state.client_name}
                    Target Profile Framework: {st.session_state.profile_framework}
                    
                    USER QUERY STRUCTURAL ROUTE:
                    {user_query}
                    
                    Provide an absolute, chronological portal filing breakdown mapping how to navigate the official portals based on this environment layout.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=agent_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are the KSP AI Compliance Agent. Your job is to process input context passed from financial sheets and client selectors "
                                "and map out structural, click-by-click government filing workflows (such as Income Tax e-filing, GSTIN, or MCA portals). "
                                "Make sure your answers reference the specific profile framework of the client to keep it customized."
                            ),
                            response_mime_type="application/json",
                            response_schema=ConnectedAgentResponse,
                            temperature=0.2
                        )
                    )
                    
                    agent_output = ConnectedAgentResponse.model_validate_json(response.text)
                    
                    st.success("✅ Connected Framework Compiled Successfully!")
                    
                    st.markdown("### 📋 Statutory Overview")
                    st.info(agent_output.statutory_overview)
                    
                    st.markdown("### ⚙️ Step-by-Step Portal Filing Mechanics")
                    for index, step in enumerate(agent_output.step_by_step_portal_workflow, 1):
                        st.markdown(f"**Step {index}:** {step}")
                        
                    col_warn, col_script = st.columns(2)
                    
                    with col_warn:
                        st.markdown("### ⚠️ Critical Audit Risks & Warnings")
                        for warning in agent_output.critical_compliance_warnings:
                            st.markdown(f"• :red[{warning}]")
                            
                    with col_script:
                        st.markdown("### 💬 Ready-to-Send Client Message Script")
                        st.text_area("Copy and paste to update your client instantly:", value=agent_output.client_communication_script, height=350)
                        
                except Exception as e:
                    st.error(f"Agent Pipeline Core Routing Error: {e}")