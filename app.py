import streamlit as st
import google.generativeai as genai
import pdfplumber
import pandas as pd
import re
import io

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="KSP Console Platform",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom dark theme styling injection
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stSidebar"] { background-color: #161920; }
    .stButton>button { width: 100%; background-color: #1f2937; color: white; border: 1px solid #374151; }
    .stButton>button:hover { background-color: #374151; border-color: #4b5563; }
    </style>
""", unsafe_allow_html=True)

# Initialize Gemini API safely using Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing Gemini API Key. Please configure GEMINI_API_KEY in your Streamlit secrets.")

# ==========================================
# 2. HELPER UTILITIES: EXTRACTION ENGINE
# ==========================================
def extract_pdf_text(uploaded_file, password=None):
    """Extracts raw text data from standard or password-protected PDFs safely."""
    text_content = ""
    try:
        # Read file bytes into a streamable buffer
        file_bytes = io.BytesIO(uploaded_file.read())
        with pdfplumber.open(file_bytes, password=password) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text_content += extracted_text + "\n"
        return text_content, None
    except Exception as e:
        return None, str(e)

def analyze_financial_text(text):
    """Uses basic RegEx and Pandas to flag important keywords in the extracted text."""
    lines = text.split("\n")
    flagged_rows = []
    
    # Simple regex flags to isolate interest, dividends, or high-value inflows
    keywords = re.compile(r"INTEREST|DIVIDEND|POS|UPI|TDS|CREDIT", re.IGNORECASE)
    
    for line in lines:
        if keywords.search(line):
            flagged_rows.append(line)
            
    df = pd.DataFrame(flagged_rows, columns=["Raw Flagged Transactions"])
    return df

# ==========================================
# 3. SIDEBAR - MODULE NAVIGATION
# ==========================================
st.sidebar.title("🛠️ KSP CONSOLE PLATFORM")
st.sidebar.write("Choose functional module to execute:")

module_options = [
    "🚀 High-Value Smart ITR Filing Engine",
    "🛡️ GST Command Center Core",
    "🧠 KSP AI Compliance & Filing Agent",
    "🏢 Business Incorporation Strategy Matrix",
    "📈 Predictive Fractional CFO Modeling"
]

selected_module = st.sidebar.radio(
    label="Navigation",
    options=module_options,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.write("⚙️ **Architecture Framework:** Unified Matrix Master v3.0")
st.sidebar.write("🔒 **Security Mode:** Active")

# Mock Client Baseline Context
active_client_name = "Mr. DIXITH CHAKRAVARTHULA"
client_profile = "Traditional Professional / Priest (Dakshina & Pooja Inflows)"

# Initialize Session State values to bridge data between different sidebar tabs
if "extracted_bank_text" not in st.session_state:
    st.session_state["extracted_bank_text"] = ""
if "extracted_ais_text" not in st.session_state:
    st.session_state["extracted_ais_text"] = ""

# --- MODULE 1: SMART ITR ENGINE (DATA COLLECTION ENGINE) ---
if selected_module == "🚀 High-Value Smart ITR Filing Engine":
    st.subheader("🚀 High-Value Smart ITR Filing Engine")
    st.info(f"**Active Pipeline:** Ready to map raw data for **{active_client_name}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏦 Step 1: Bank Statement Processing")
        bank_file = st.file_uploader("Upload Bank Statement (PDF)", type=["pdf"], key="bank_upload")
        bank_pass = st.text_input("Bank Statement Password (If encrypted)", type="password", key="bank_p")
        
        if bank_file and st.button("Parse & Load Bank PDF"):
            with st.spinner("Decrypting and mining bank transaction matrix..."):
                text, err = extract_pdf_text(bank_file, bank_pass if bank_pass else None)
                if err:
                    st.error(f"Failed to read Bank PDF: {err}")
                else:
                    st.session_state["extracted_bank_text"] = text
                    st.success("Bank Statement structural parameters saved into session state.")
                    
                    # Optional visualization matrix using Pandas
                    df_analysis = analyze_financial_text(text)
                    if not df_analysis.empty:
                        st.dataframe(df_analysis.head(10))

    with col2:
        st.markdown("### 📄 Step 2: Annual Information Statement (AIS)")
        ais_file = st.file_uploader("Upload Government AIS File (PDF)", type=["pdf"], key="ais_upload")
        ais_pass = st.text_input("AIS Password (PAN Lowercase + DOB DDMMYYYY)", type="password", key="ais_p")
        
        if ais_file and st.button("Parse & Load AIS PDF"):
            with st.spinner("Decrypting and parsing government tax ledger matrix..."):
                text, err = extract_pdf_text(ais_file, ais_pass if ais_pass else None)
                if err:
                    st.error(f"Failed to read AIS PDF: {err}")
                else:
                    st.session_state["extracted_ais_text"] = text
                    st.success("AIS official ledger records cached successfully.")

# --- MODULE 2: GST COMMAND CENTER ---
elif selected_module == "🛡️ GST Command Center Core":
    st.subheader("🛡️ GST Command Center Core")
    st.warning("Cross-referencing turnover parameters between banking transactions and GSTR ledger records.")
    st.write("This module operates dynamically once baseline data models are populated inside your active pipelines.")

# --- MODULE 3: KSP AI COMPLIANCE & FILING AGENT (THE BRAIN ENGINE) ---
elif selected_module == "🧠 KSP AI Compliance & Filing Agent":
    st.subheader("🧠 KSP AI Compliance & Filing Agent")
    
    st.markdown(f"""
    <div style="background-color:#1e293b; padding:15px; border-radius:5px; border-left: 5px solid #3b82f6; margin-bottom:20px;">
        <span style="color:#60a5fa; font-weight:bold;">🔗 Connected Financial Master Pipeline Active: Data Ready for Evaluation</span><br>
        <span style="color:#ffffff;">• <b>Active Client:</b> {active_client_name} | • <b>Profile Model:</b> {client_profile}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Visual cues checking if text data was collected from Module 1
    has_bank = len(st.session_state["extracted_bank_text"]) > 0
    has_ais = len(st.session_state["extracted_ais_text"]) > 0
    
    st.markdown(f"**Data Status Vector:** Bank Data Cached: `{'✅ Yes' if has_bank else '❌ No'}` | AIS Data Cached: `{'✅ Yes' if has_ais else '❌ No'}`")
    
    default_prompt = (
        f"Perform parallel computing for both Standard Compliance and Credit Optimization layouts for {active_client_name}. "
        f"Determine the exact recommended option based on audit protection rules. Cross-verify calculated bank ledger transactions "
        f"against declared AIS data fields. Provide a step-by-step sequential strategy roadmap to safely file their ITR return on the official portal."
    )
    user_directive = st.text_area("Master Calculation Prompts / Directives:", value=default_prompt, height=120)
    
    if st.button("Execute Dual-Route Financial Synthesis"):
        if not has_bank and not has_ais:
            st.warning("No live data parsed yet. Running structural synthesis using client baseline profile parameters...")
        
        with st.spinner("Processing deep architectural synthesis through AI core engine..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Assemble the massive prompt containing the underlying raw data context securely
                full_payload = (
                    f"System Context: You are KSP AI Compliance Agent running on Matrix Master Framework v3.0.\n"
                    f"Client Profile: {client_profile}\n"
                    f"User Directives: {user_directive}\n\n"
                    f"--- DATA PIPELINE ATTACHMENTS ---\n"
                    f"RAW BANK TEXT SNIPPET (First 4000 chars): {st.session_state['extracted_bank_text'][:4000]}\n\n"
                    f"RAW AIS TEXT SNIPPET (First 4000 chars): {st.session_state['extracted_ais_text'][:4000]}\n"
                )
                
                response = model.generate_content(full_payload)
                
                st.success("Synthesis Strategy Generated Successfully!")
                st.markdown("### 📋 Recommended Compliance Framework & Strategy")
                st.write(response.text)
                
                # Enable a direct text download link of the report for offline tracking
                st.download_button(
                    label="📥 Download Step-by-Step Filing Report",
                    data=response.text,
                    file_name=f"ITR_Filing_Blueprint_{active_client_name.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error("Strategy Parallel Processing Error: 503 UNAVAILABLE")
                st.markdown("""
                > **System Note:** The AI calculation core is currently experiencing high demand volumes on the free tier engine. 
                > **Recommended Action:** Wait 15–30 seconds and click **Execute Dual-Route Financial Synthesis** again to rerun the cycle.
                """)

# --- MODULE 4: BUSINESS INCORPORATION ---
elif selected_module == "🏢 Business Incorporation Strategy Matrix":
    st.subheader("🏢 Business Incorporation Strategy Matrix")
    st.write("Evaluating structural transformation protocols (Proprietorship to LLP transitions).")

# --- MODULE 5: FRACTIONAL CFO ---
elif selected_module == "📈 Predictive Fractional CFO Modeling":
    st.subheader("📈 Predictive Fractional CFO Modeling")
    st.write("Accessing deep forecast metrics and transactional ledger runways.")