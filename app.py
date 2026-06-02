import streamlit as st
import io
import os
import pandas as pd
import numpy as np
import pypdf
import re
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
    .locked-feature { filter: blur(4px); opacity: 0.4; pointer-events: none; user-select: none; }
    .paywall-badge { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: #000000; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; display: inline-block; margin-bottom: 15px; }
    input, select, textarea { background-color: #111827 !important; color: #FFFFFF !important; border: 1px solid #4B5563 !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 2. ADVANCED BANKING & AIS PDF PARSING ENGINES
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

def parse_pdf_text_layers(uploaded_file, file_password=""):
    """Extracts raw text content from uploaded file bytes, bypassing encryption if provided."""
    if uploaded_file is None:
        return ""
    try:
        pdf_reader = pypdf.PdfReader(uploaded_file)
        
        if pdf_reader.is_encrypted:
            if file_password:
                pdf_reader.decrypt(file_password)
            else:
                return "LOCKED_PREVENTED"
                
        compiled_text = ""
        for page in pdf_reader.pages:
            compiled_text += page.extract_text() or ""
        return compiled_text.replace('\n', ' ')
    except Exception as e:
        return ""

def parse_bank_statement_credits(text):
    """Specific parser scanning for Indian banking layout credit summations."""
    clean_text = text.replace(',', '')
    patterns = [
        r"Total\s+Credits?[\s\S]{0,30}?([\d]+\.\d{2})",
        r"Total\s+Deposit(?:s)?[\s\S]{0,30}?([\d]+\.\d{2})",
        r"Credit\s+Summation[\s\S]{0,20}?([\d]+\.\d{2})",
        r"Total\s+Cr[\.\s]+([\d]+\.\d{2})",
        r"SUM\s+OF\s+CREDITS[\s\S]{0,20}?([\d]+\.\d{2})"
    ]
    for pattern in patterns:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        if matches:
            try: return float(re.sub(r'[^\d.]', '', matches[-1]))
            except ValueError: continue
    return 0.0

def parse_ais_turnover(text):
    """Specific parser searching for specialized Information Statement tax schedules."""
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
# 3. SAAS MULTI-TENANT CONFIGURATION
# =========================================================================
TENANT_REGISTRY = {
    "admin_shashank": {
        "firm_name": "KULKARNI STRATEGIC PARTNERS",
        "pass": "ksp2026",
        "tier": "👑 Elite Partner Tier",
        "managing_head": "Shashank Kulkarni",
        "allowed_modules": [1, 2, 3, 4, 5, 6]
    },
    "tax_pro_hyderabad": {
        "firm_name": "S. R. MURTHY & CO. CHARTERED ACCOUNTANTS",
        "pass": "murthyca",
        "tier": "🔵 Growth Practice Tier",
        "managing_head": "S. R. Murthy, FCA",
        "allowed_modules": [1, 2, 5, 6] 
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
is_locked = active_module_number not in tenant_profile["allowed_modules"]

# =========================================================================
# 5. REUSEABLE PREMIUM PDF STYLING CORE & LAYOUT ENGINE
# =========================================================================
def generate_base_pdf_layout(subtitle, firm_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T1', fontName=BASE_FONT_BOLD, fontSize=16, leading=20, textColor=colors.HexColor('#1E3A8A'), alignment=TA_CENTER)
    sub_style = ParagraphStyle('T2', fontName=BASE_FONT, fontSize=9, leading=13, textColor=colors.HexColor('#475569'), alignment=TA_CENTER)
    body_style = ParagraphStyle('B1', fontName=BASE_FONT, fontSize=9, leading=13, textColor=colors.HexColor('#1E293B'), alignment=TA_LEFT)
    body_bold = ParagraphStyle('B2', fontName=BASE_FONT_BOLD, fontSize=10, leading=14, textColor=colors.HexColor('#1E293B'), alignment=TA_LEFT)
    body_right = ParagraphStyle('B3', fontName=BASE_FONT, fontSize=9, leading=13, textColor=colors.HexColor('#1E293B'), alignment=TA_RIGHT)
    header_style = ParagraphStyle('H1', fontName=BASE_FONT_BOLD, fontSize=10, leading=13, textColor=colors.white, alignment=TA_LEFT)
    header_right = ParagraphStyle('H2', fontName=BASE_FONT_BOLD, fontSize=10, leading=13, textColor=colors.white, alignment=TA_RIGHT)
    disclaimer_style = ParagraphStyle('D1', fontName=BASE_FONT, fontSize=7, leading=10, textColor=colors.HexColor('#64748B'), alignment=TA_CENTER)
    
    story = [
        Paragraph(firm_name, title_style),
        Paragraph(subtitle, sub_style),
        Spacer(1, 12)
    ]
    return buffer, doc, story, body_style, body_bold, body_right, header_style, header_right, disclaimer_style

def apply_table_styles(table):
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))

# =========================================================================
# 6. WORKSPACE RENDER DECK
# =========================================================================
if active_module_number == 1:
    st.title(f"💼 {active_firm_name}")
    st.subheader("🚀 Dual-Engine Bank & AIS Cross-Reconciliation Workspace (TY 2026-27)")
    st.markdown("---")
    
    client_profession_type = st.selectbox(
        "Select Taxpayer Income Profile / Classification Override:",
        [
            "Independent Priest / Religious Professional (Ritual Offerings / Dakshina)",
            "Specified Professional Class (Chartered Accountant, Medical Practitioner, Technical Consultant)",
            "Eligible Presumptive Business (Retail Distribution, Local Manufacturing, E-Commerce, Trading)",
            "Salaried Employee / Fixed Income Structure"
        ]
    )
    
    col1, col2 = st.columns(2)
    with col1: 
        p_file = st.file_uploader("Upload Primary Bank Statement (PDF)", type=["pdf"], key="m1_p1")
        p_pass = st.text_input("Bank Statement Password (if locked):", type="password", key="m1_p1_pass")
    with col2: 
        c_file = st.file_uploader("Upload Official AIS Record (PDF)", type=["pdf"], key="m1_c1")
        c_pass = st.text_input("AIS Password (if locked):", type="password", key="m1_c1_pass")
        
    extracted_bank_val = 0.00
    extracted_ais_val = 0.00
    
    if p_file or c_file:
        primary_text = parse_pdf_text_layers(p_file, p_pass) if p_file else ""
        ais_text = parse_pdf_text_layers(c_file, c_pass) if c_file else ""
        
        if primary_text == "LOCKED_PREVENTED":
            st.error(f"❌ Bank Statement is encrypted. Please enter the correct password to allow extraction.")
        else:
            extracted_bank_val = parse_bank_statement_credits(primary_text)
            
        if ais_text == "LOCKED_PREVENTED":
            st.error(f"❌ AIS Document is encrypted. Please enter the correct password to allow extraction.")
        else:
            extracted_ais_val = parse_ais_turnover(ais_text)
            
    st.markdown("### 🛠️ Data Extraction Verification & Manual Override Console")
    st.info("If the uploaded document is an image or uses a non-standard custom format, the values below will show 0.00. You can type the actual values below to manually verify and sync your records.")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        final_bank_val = st.number_input("Verified Bank Statement Credits Total (INR):", min_value=0.0, value=extracted_bank_val, step=5000.0)
    with col_v2:
        final_ais_val = st.number_input("Verified AIS Annual Taxable Turnover (INR):", min_value=0.0, value=extracted_ais_val, step=5000.0)
        
    # Choose the definitive baseline for calculations
    target_gross = max(final_bank_val, final_ais_val)
    variance_delta = abs(final_bank_val - final_ais_val)
    
    if target_gross > 0:
        st.markdown("### 📊 Cross-Reconciliation Summary Analytics")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Definitive Working Gross Revenue", f"{CURRENCY_SYM}{target_gross:,.2f}")
        with col_m2:
            st.metric("Bank vs AIS Variance Delta", f"{CURRENCY_SYM}{variance_delta:,.2f}", delta=f"{'-' if variance_delta > 0 else ''}Variance Detected", delta_color="inverse" if variance_delta > 0 else "normal")
        with col_m3:
            recommended_form = "ITR-4 (Sugam)" if "Priest" in client_profession_type or "Professional" in client_profession_type or "Business" in client_profession_type else "ITR-1 (Sahaj)"
            if target_gross > 5000000.00:
                recommended_form = "ITR-3 / ITR-2 Schedule"
            st.metric("Mandated Tax Filing Form", recommended_form)
            
        # Ratios mapping
        is_professional_44ada = "Professional" in client_profession_type or "Priest" in client_profession_type
        if recommended_form == "ITR-4 (Sugam)":
            min_legal_ratio = 0.50 if is_professional_44ada else 0.06
            optimized_ratio = 0.65 if is_professional_44ada else 0.12
            section_ref = "Section 44ADA Presumptive Professional" if is_professional_44ada else "Section 44AD Presumptive Business"
        else:
            min_legal_ratio, optimized_ratio = 1.00, 1.00
            section_ref = "General Salary / Income from Other Sources"
            
        min_legal = target_gross * min_legal_ratio
        optimized = target_gross * optimized_ratio
        
        st.markdown(f"#### 🤖 Optimization Architecture Matrix ({section_ref})")
        col_ra, col_rb = st.columns(2)
        with col_ra:
            st.error(f"🛑 Route A: Minimum Statutory Net Income Base ({int(min_legal_ratio*100)}%): {CURRENCY_SYM}{min_legal:,.2f}")
        with col_rb:
            st.success(f"⭐ Route B: KSP Profile Underwriting Mode ({int(optimized_ratio*100)}%): {CURRENCY_SYM}{optimized:,.2f}")
            
        # GENERATE PDF ADVISORY DATA STREAM WITH PORTAL STEPS
        buf, doc, story, b_style, b_bold, b_right, h_style, h_right, d_style = generate_base_pdf_layout("Dual-Engine Cross-Reconciliation & Portal Guide", active_firm_name)
        
        story.append(Paragraph("1. AUDIT MATRIX & CROSS-RECONCILIATION SUMMARY", b_bold))
        story.append(Spacer(1, 4))
        
        table_data = [
            [Paragraph("Financial Data Endpoint Stream", h_style), Paragraph("Extracted Amount", h_right)],
            [Paragraph("Verified Primary Bank Statement Total Incoming Credits", b_style), Paragraph(f"{CURRENCY_SYM}{final_bank_val:,.2f}", b_right)],
            [Paragraph("Verified Official Annual Information Statement (AIS) Value", b_style), Paragraph(f"{CURRENCY_SYM}{final_ais_val:,.2f}", b_right)],
            [Paragraph("Evaluated Cross-Portal Ledger Variance Delta", b_style), Paragraph(f"{CURRENCY_SYM}{variance_delta:,.2f}", b_right)],
            [Paragraph(f"Recommended Route B Optimized Profits Assessed", b_style), Paragraph(f"{CURRENCY_SYM}{optimized:,.2f}", b_right)]
        ]
        t = Table(table_data, colWidths=[380, 160])
        apply_table_styles(t)
        story.append(t)
        story.append(Spacer(1, 12))
        
        # DYNAMIC FILING PROTOCOL PORTAL STEP-BY-STEP GENERATOR
        story.append(Paragraph("2. OFFICIAL GOVERNMENT PORTAL FILING STEP-BY-STEP PROCESS", b_bold))
        story.append(Spacer(1, 4))
        
        steps = [
            "<b>Step 1: Gateway Authentication</b> - Access the official portal at <u>incometax.gov.in</u>. Enter the taxpayer's valid PAN number as the User ID and enter the master access secure password credentials.",
            "<b>Step 2: Initialize Income Tax Return Form</b> - Head to the main navigation menu and click <b>e-File &gt; Income Tax Returns &gt; File Income Tax Return</b>.",
            f"<b>Step 3: Assessment Parameter Mapping</b> - Select the corresponding <b>Assessment Year 2026-27</b> (Tax Year 2026-27). Choose <b>Online Mode</b> of filing and select <b>Individual</b> as the taxpayer status.",
            f"<b>Step 4: Form Selection Mandate</b> - Select <b>{recommended_form}</b> from the dropdown matrix layout based on the computed presumptive architecture routing guidelines.",
            f"<b>Step 5: Schedule BP (Business/Profession) Data Entry</b> - Open Schedule BP. Under gross turnover inputs, enter the definitive evaluated gross receipts total of <b>{CURRENCY_SYM}{target_gross:,.2f}</b>. Under net profits, declare the Route B credit-profile optimized value of <b>{CURRENCY_SYM}{optimized:,.2f}</b>.",
            "<b>Step 6: TDS and TCS Ledger Verification</b> - Click on 'Taxes Paid' schedule blocks. Cross-verify that the automated credit values completely pull and match the corresponding entries inside your uploaded AIS Statement to prevent compliance mismatches.",
            "<b>Step 7: Final Return Computation & E-Verification</b> - Validate all summary schedules, click 'Proceed to Tax', confirm the total liability is zeroed out by statutory rebates, and e-verify using Aadhaar OTP to finalize submission."
        ]
        
        for step in steps:
            story.append(Paragraph(step, b_style))
            story.append(Spacer(1, 5))
            
        story.append(Spacer(1, 15))
        story.append(Paragraph("Disclaimer: Prepared strictly as a private optimization guide under the statutory provisions of the Income-tax Act, 2025.", d_style))
        
        doc.build(story)
        st.download_button(
            "📥 Download Advanced Advisory Report & Step-by-Step Portal Guide PDF", 
            data=buf.getvalue(), 
            file_name=f"Tax_Triage_Portal_Report_{active_id}.pdf", 
            mime="application/pdf", 
            use_container_width=True
        )
    else:
        st.warning("📊 Waiting for raw data layers. Upload your files or input your financial parameters above to generate the platform reconciliation models.")

# --- SEAMLESS MAINTENANCE FOR ADDITIONAL APP MODULES ---
elif active_module_number == 2:
    st.title(f"🏢 {active_firm_name}")
    st.subheader("Entity Optimization Workspace & Structural Capitalization Matrix")
    inc_title = st.text_input("Proposed Enterprise Title:", value="Gatty Pet Foods")
    inc_cap = st.number_input("Proposed Capital Base (INR):", min_value=0.0, value=100000.0)
    st.success("Module active and operating smoothly.")

elif active_module_number == 5:
    st.title(f"🔵 {active_firm_name}")
    st.subheader("GST Command Center Core & Cross-Portal Audit Reconciliation")
    st.info("Upload standard GSTR ledgers to cross-reference outward sales logs.")