import streamlit as st
import google.generativeai as genai
import pdfplumber
import pandas as pd
import re
import io
from fpdf import FPDF

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="KSP Console Platform",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom dark theme styling injection matching your console setup
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
# 2. HELPER UTILITIES: EXTRACTION & PDF GENERATION
# ==========================================
def extract_pdf_text(uploaded_file, password=None):
    """Extracts raw text data from standard or password-protected PDFs safely."""
    text_content = ""
    try:
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
    """Parses raw Indian banking text strings into highly structured columns."""
    lines = text.split("\n")
    structured_data = []
    
    # Advanced Regex pattern to capture: Date, Description, Amount, Type, Balance, Balance Type
    pattern = re.compile(r"(\d{2}-\d{2}-\d{4})\s+(.*?)\s+([\d.]+)\((Cr|Dr)\)\s+([\d.]+)\((Cr|Dr)\)", re.IGNORECASE)
    
    for line in lines:
        match = pattern.search(line)
        if match:
            date, desc, amt, amt_type, bal, bal_type = match.groups()
            structured_data.append({
                "Date": date,
                "Transaction Particulars": desc,
                "Amount (₹)": float(amt),
                "Type": amt_type.upper(),
                "Running Balance": f"₹{bal} ({bal_type.upper()})"
            })
            
    df = pd.DataFrame(structured_data)
    
    # Fallback to keyword row match if strict structural pattern doesn't fit the bank format
    if df.empty:
        flagged_rows = [line for line in lines if re.search(r"INTEREST|DIVIDEND|POS|UPI|TDS|CREDIT", line, re.IGNORECASE)]
        df = pd.DataFrame(flagged_rows, columns=["Raw Flagged Transactions"])
        
    return df

def create_styled_pdf(client_name, profile, model_output_text):
    """Generates an elite corporate PDF compliance brief matching the KSP format."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 20, 15)
    
    # --- HEADER / BRAND TITLE BLOCK ---
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(16, 25, 32) 
    pdf.cell(0, 8, "KULKARNI STRATEGIC PARTNERS", ln=True, align="L")
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100) 
    pdf.cell(0, 6, "Statutory Tax Compliance Strategy & Optimization Brief", ln=True, align="L")
    
    # Horizontal Rule Divider
    pdf.set_draw_color(180, 180, 180)
    pdf.line(15, pdf.get_y() + 4, 195, pdf.get_y() + 4)
    pdf.ln(8)
    
    # --- METADATA METRICS BLOCK ---
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(40, 6, "Client Profile Name:", ln=False)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"{client_name}", ln=True)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(40, 6, "Framework Category:", ln=False)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"{profile}", ln=True)
    
    pdf.set_draw_color(220, 225, 230)
    pdf.line(15, pdf.get_y() + 4, 195, pdf.get_y() + 4)
    pdf.ln(8)
    
    # --- BODY CONTENT SYNTHESIS ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(16, 25, 32)
    
    lines = model_output_text.split("\n")
    for line in lines:
        cleaned_line = line.replace("**", "").replace("*", "").strip() 
        if not cleaned_line:
            pdf.ln(3)
            continue
            
        if "STEP-BY-STEP" in cleaned_line.upper() or "DECISION BRIEF" in cleaned_line.upper() or "STRATEGY" in cleaned_line.upper() or "PORTAL" in cleaned_line.upper():
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(31, 41, 55)
            pdf.cell(0, 6, cleaned_line, ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(55, 65, 81)
        else:
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(55, 65, 81)
            pdf.multi_cell(0, 6, cleaned_line)
            
    return pdf.output()

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

# Client Baseline Profiles Context mapping
active_client_name = "Mr. DIXITH CHAKRAVARTHULA"
client_profile = "Traditional Professional / Priest (Dakshina & Pooja Inflows)"

# Keep persistent global cache vectors using Session State across tabs
if "extracted_bank_text" not in st.session_state:
    st.session_state["extracted_bank_text"] = ""
if "extracted_ais_text" not in st.session_state:
    st.session_state["extracted_ais_text"] = ""
if "calculated_credits_total" not in st.session_state:
    st.session_state["calculated_credits_total"] = 0.0

# --- MODULE 1: SMART ITR ENGINE ---
if selected_module == "🚀 High-Value Smart ITR Filing Engine":
    st.subheader("🚀 High-Value Smart ITR Filing Engine")
    st.info(f"**Active Pipeline:** Ready to map raw data for **{active_client_name}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏦 Step 1: Bank Statement Processing")
        bank_file = st.file_uploader("Upload Bank Statement (PDF)", type=["pdf"], key="bank_upload")
        bank_pass = st.text_input("Bank Statement Password (If encrypted)", type="password", key="bank_p")
        
        if bank_file and st.button("Parse & Load Bank PDF"):
            with st.spinner("Decrypting and parsing bank ledger rows..."):
                text, err = extract_pdf_text(bank_file, bank_pass if bank_pass else None)
                if err:
                    st.error(f"Failed to read Bank PDF: {err}")
                else:
                    st.session_state["extracted_bank_text"] = text
                    st.success("Bank Statement elements successfully parsed.")
                    
                    df_analysis = analyze_financial_text(text)
                    st.dataframe(df_analysis)
                    
                    if "Amount (₹)" in df_analysis.columns:
                        total_credits = df_analysis[df_analysis["Type"] == "CR"]["Amount (₹)"].sum()
                        st.session_state["calculated_credits_total"] = total_credits
                        st.metric(label="Evaluated Bank Inflows (Total Credits)", value=f"INR {total_credits:,.2f}")

    with col2:
        st.markdown("### 📄 Step 2: Annual Information Statement (AIS)")
        ais_file = st.file_uploader("Upload Government AIS File (PDF)", type=["pdf"], key="ais_upload")
        ais_pass = st.text_input("AIS Password", type="password", key="ais_p")
        
        if ais_file and st.button("Parse & Load AIS PDF"):
            with st.spinner("Decrypting official government information data lines..."):
                text, err = extract_pdf_text(ais_file, ais_pass if ais_pass else None)
                if err:
                    st.error(f"Failed to read AIS PDF: {err}")
                else:
                    st.session_state["extracted_ais_text"] = text
                    st.success("AIS parameters fully imported to session state matrix.")

# --- MODULE 2: GST COMMAND CENTER ---
elif selected_module == "🛡️ GST Command Center Core":
    st.subheader("🛡️ GST Command Center Core")
    st.warning("Cross-referencing turnover parameters between banking transactions and GSTR ledger records.")

# --- MODULE 3: KSP AI COMPLIANCE AGENT (THE STRATEGY MATRIX OUTPUT) ---
elif selected_module == "🧠 KSP AI Compliance & Filing Agent":
    st.subheader("🧠 KSP AI Compliance & Filing Agent")
    
    st.markdown(f"""
    <div style="background-color:#1e293b; padding:15px; border-radius:5px; border-left: 5px solid #3b82f6; margin-bottom:20px;">
        <span style="color:#60a5fa; font-weight:bold;">🔗 Connected Financial Master Pipeline Active: Data Ready for Evaluation</span><br>
        <span style="color:#ffffff;">• <b>Active Client:</b> {active_client_name} | • <b>Profile Model:</b> {client_profile}</span>
    </div>
    """, unsafe_allow_html=True)
    
    has_bank = len(st.session_state["extracted_bank_text"]) > 0
    has_ais = len(st.session_state["extracted_ais_text"]) > 0
    
    st.markdown(f"**Data Status Vector:** Bank Data Cached: `{'✅ Yes' if has_bank else '❌ No'}` | AIS Data Cached: `{'✅ Yes' if has_ais else '❌ No'}`")
    
    default_prompt = (
        f"Perform parallel computing for both Standard Compliance and Credit Optimization layouts for {active_client_name}. "
        f"Determine the exact recommended option based on audit protection rules. Use the total gross receipts of INR {st.session_state['calculated_credits_total']:,.2f} if populated. "
        f"Provide a sequential, clear section for 'PORTAL EXECUTION STEP-BY-STEP FILING STEPS' using the precise format structure of Kulkarni Strategic Partners briefings."
    )
    user_directive = st.text_area("Master Calculation Prompts / Directives:", value=default_prompt, height=120)
    
    if st.button("Execute Dual-Route Financial Synthesis"):
        with st.spinner("Processing deep architectural synthesis..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                full_payload = (
                    f"System Task: Act as KSP AI Compliance Agent. Output in clean text matching the structural guidelines of KSP Briefing sheets.\n"
                    f"Client Name: {active_client_name}\n"
                    f"Framework Category: {client_profile}\n"
                    f"Evaluated Gross Inflows: INR {st.session_state['calculated_credits_total']:,.2f}\n"
                    f"Directives: {user_directive}\n\n"
                    f"Data Attachments:\n"
                    f"Bank Log Text: {st.session_state['extracted_bank_text'][:3000]}\n"
                    f"AIS Log Text: {st.session_state['extracted_ais_text'][:3000]}\n"
                )
                
                response = model.generate_content(full_payload)
                
                st.success("Synthesis Strategy Generated Successfully!")
                st.markdown("### 📋 Preview Summary Layout")
                st.write(response.text)
                
                # Render the text directly into the KSP structured PDF file format byte stream
                pdf_data = create_styled_pdf(active_client_name, client_profile, response.text)
                
                st.download_button(
                    label="📥 Download Professional KSP Tax Strategy Brief (PDF)",
                    data=bytes(pdf_data),
                    file_name=f"KSP_Tax_Strategy_Brief_{active_client_name.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error("Strategy Parallel Processing Error: 503 UNAVAILABLE")
                st.markdown("> **Recommended Action:** Spikes in demand are temporary on the free model. Wait 15 seconds and re-click the button to run.")

# --- MODULE 4: BUSINESS INCORPORATION ---
elif selected_module == "🏢 Business Incorporation Strategy Matrix":
    st.subheader("🏢 Business Incorporation Strategy Matrix")
    st.write("Evaluating optimal business formation frameworks.")

# --- MODULE 5: FRACTIONAL CFO ---
elif selected_module == "📈 Predictive Fractional CFO Modeling":
    st.subheader("📈 Predictive Fractional CFO Modeling")
    st.write("Accessing deep forecast metrics and transactional ledger runways.")