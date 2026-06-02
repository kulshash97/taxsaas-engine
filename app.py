import streamlit as st
import io
import os
import pandas as pd
import numpy as np
import pypdf
import re
import google.generativeai as genai
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# =========================================================================
# 1. GLOBAL PLATFORM INITIALIZATION & PREMIUM DARK SLATE THEME (CSS)
# =========================================================================
st.set_page_config(
    layout="wide", 
    page_title="KSP Core | Premium SaaS Interface", 
    initial_sidebar_state="expanded"
)

# Custom Institutional Dark-Sleek CSS Injector
st.markdown("""
<style>
    .stApp { background-color: #0B0F19; color: #E2E8F0; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1F2937; }
    div[data-testid='stSidebarNav'] {display: none;}
    div[data-testid="stContainer"] { background-color: #1F2937; border: 1px solid #374151 !important; border-radius: 10px; padding: 20px; }
    input, select, textarea { background-color: #111827 !important; color: #FFFFFF !important; border: 1px solid #4B5563 !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 2. ADVANCED BANKING & AIS PDF PARSING ENGINES (NO PASSWORD ENCRYPTION)
# =========================================================================
CURRENCY_SYM = "INR "
BASE_FONT = "Helvetica"
BASE_FONT_BOLD = "Helvetica-Bold"

try:
    if os.path.exists("NotoSans-Regular.ttf") and os.path.exists("NotoSans-Bold.ttf"):
        pdfmetrics.registerFont(TTFont('NotoSans', 'NotoSans-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('NotoSans-Bold', 'NotoSans-Bold.ttf'))
        BASE_FONT = "NotoSans"
        BASE_FONT_BOLD = "NotoSans-Bold"
        CURRENCY_SYM = "₹"
except Exception:
    pass

def parse_pdf_text_layers(uploaded_file):
    """Extracts raw text characters from unlocked or saved PDF files directly."""
    if uploaded_file is None:
        return ""
    try:
        pdf_reader = pypdf.PdfReader(uploaded_file)
        compiled_text = ""
        for page in pdf_reader.pages:
            compiled_text += page.extract_text() or ""
        return compiled_text.replace('\n', ' ')
    except Exception:
        return ""

def parse_bank_statement_credits(text):
    """Specific parser scanning for Indian banking layout credit summations."""
    if not text:
        return 0.0
    clean_text = text.replace(',', '')
    patterns = [
        r"Total\s+Credits?[\s\S]{0,40}?([\d]+\.\d{2})",
        r"Total\s+Deposit(?:s)?[\s\S]{0,40}?([\d]+\.\d{2})",
        r"Credit\s+Summation[\s\S]{0,30}?([\d]+\.\d{2})",
        r"Total\s+Cr[\.\s]+([\d]+\.\d{2})",
        r"SUM\s+OF\s+CREDITS[\s\S]{0,30}?([\d]+\.\d{2})"
    ]
    for pattern in patterns:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        if matches:
            try: return float(re.sub(r'[^\d.]', '', matches[-1]))
            except ValueError: continue
    return 0.0

def parse_ais_turnover(text):
    """Specific parser searching for specialized Information Statement tax schedules."""
    if not text:
        return 0.0
    clean_text = text.replace(',', '')
    patterns = [
        r"Business\s+receipts[\s\S]{0,50}?([\d]+\.\d{2})",
        r"Receipts\s+under\s+Section\s+194J[\s\S]{0,50}?([\d]+\.\d{2})",
        r"Total\s+Value\s*[\s:;]+\s*([\d]+\.\d{2})",
        r"Amount\s+Paid/Credited[\s\S]{0,40}?([\d]+\.\d{2})",
        r"Gross\s+Salary[\s\S]{0,30}?([\d]+\.\d{2})"
    ]
    for pattern in patterns:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        if matches:
            try: return float(re.sub(r'[^\d.]', '', matches[-1]))
            except ValueError: continue
    return 0.0

# =========================================================================
# 2B. GOOGLE GEMINI DEEP AUDIT LAYER CONFIGURATION
# =========================================================================
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
elif "gemini_api_key" in st.secrets:
    genai.configure(api_key=st.secrets["gemini_api_key"])

def get_gemini_reconciliation(bank_text, ais_text):
    """Sends raw string data directly to Gemini for deep schema reconciliation."""
    if not bank_text and not ais_text:
        return None
        
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are an expert AI Indian Chartered Accountant. Cross-verify and reconcile the following text layers extracted from a client's Bank Statement and Annual Information Statement (AIS).
    
    BANK STATEMENT TEXT:
    {bank_text}
    
    AIS TEXT:
    {ais_text}
    
    Instructions:
    1. Extract total bank credits and total AIS income reported. Calculate the absolute variance.
    2. Create a step-by-step transaction audit trail matching specific income components or entries between both data sources.
    3. Generate a sequential, clean set of steps with exact filing parameters to type into the clear Indian Income Tax (ITR) Portal.
    
    Output format: You MUST respond ONLY with a valid, clean JSON object matching the schema below. No conversational text filler, no markdown wrappers outside the JSON block.
    {{
      "client_summary": {{
        "total_bank_credits": 0.0,
        "total_ais_reported": 0.0,
        "variance": 0.0,
        "status": "Verified / Variance Found"
      }},
      "reconciliation_table": [
        {{"step": "Step 1", "description": "Verified receipts matching 194J schedule", "bank_amount": 0.0, "ais_amount": 0.0, "variance": 0.0}}
      ],
      "itr_filing_steps": [
        {{"step_number": 1, "portal_section": "Schedule BP (Business & Profession) / Presumptive 44ADA", "action_required": "Input exact declared professional income matching AIS records", "exact_amount_to_enter": 0.0}}
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        st.error(f"Gemini Processing Exception: {str(e)}")
        return None

# =========================================================================
# 3. SAAS MULTI-TENANT CONFIGURATION
# =========================================================================
TENANT_REGISTRY = {
    "admin_shashank": {
        "firm_name": "KULKARNI STRATEGIC PARTNERS",
        "pass": "ksp2026",
        "tier": "👑 Elite Partner Tier",
        "managing_head": "Shashank Kulkarni",
        "allowed_modules": [1, 2, 3, 4, 5, 6]
    }
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "tenant_id" not in st.session_state:
    st.session_state["tenant_id"] = None

# =========================================================================
# 4. SIDEBAR CONSOLE GATEWAY
# =========================================================================
st.sidebar.title("🔐 KSP SAAS ACCESS CONSOLE")

if not st.session_state["authenticated"]:
    input_user = st.sidebar.text_input("Tenant User ID:", key="auth_user")
    input_pass = st.sidebar.text_input("Access Password:", type="password", key="auth_pass")
    if st.sidebar.button("Authenticate Platform Node", use_container_width=True):
        if input_user in TENANT_REGISTRY and TENANT_REGISTRY[input_user]["pass"] == input_pass:
            st.session_state["authenticated"] = True
            st.session_state["tenant_id"] = input_user
            st.rerun()
        else:
            st.sidebar.error("❌ Access Token Invalid.")
    st.stop()
else:
    active_id = st.session_state["tenant_id"]
    tenant_profile = TENANT_REGISTRY[active_id]
    st.sidebar.success(f"🔒 Node: {active_id}")
    st.sidebar.markdown(f"**🏢 Enterprise:**\n`{tenant_profile['firm_name']}`")
    if st.sidebar.button("Disconnect Session Node", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["tenant_id"] = None
        st.rerun()

st.sidebar.markdown("---")
module_options_map = {
    "🚀 Module 1: Smart ITR Filing Engine": 1,
    "🏢 Module 2: Business Incorporation Strategy": 2,
    "🔵 Module 5: GST Command Center Core": 5,
    "📈 Module 6: Predictive Fractional CFO Model": 6
}
module_selection = st.sidebar.radio("Navigate Workspace", options=list(module_options_map.keys()), label_visibility="collapsed")
active_module_number = module_options_map[module_selection]
active_firm_name = tenant_profile["firm_name"]

# =========================================================================
# 5. PREMIUM PDF STYLING CORE & REPORTLAB LAYOUT COMPILER ENGINE
# =========================================================================
def compile_reportlab_pdf(gemini_data, firm_name):
    """Generates an elite-tier structured audit reconciliation PDF in-memory."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T1', fontName=BASE_FONT_BOLD, fontSize=16, leading=20, textColor=colors.HexColor('#1E3A8A'), alignment=TA_CENTER)
    sub_style = ParagraphStyle('T2', fontName=BASE_FONT, fontSize=9, leading=13, textColor=colors.HexColor('#475569'), alignment=TA_CENTER)
    body_style = ParagraphStyle('B1', fontName=BASE_FONT, fontSize=9, leading=13, textColor=colors.HexColor('#1E293B'), alignment=TA_LEFT)
