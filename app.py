import streamlit as st
import io
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

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
    /* Main Background & Fonts */
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
    }
    /* Sidebar Overrides */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
    }
    div[data-testid='stSidebarNav'] {display: none;}
    
    /* Container & Card Styling */
    div[data-testid="stContainer"] {
        background-color: #1F2937;
        border: 1px solid #374151 !important;
        border-radius: 10px;
        padding: 20px;
    }
    /* Paywall / Locked Element Blurring Effect */
    .locked-feature {
        filter: blur(4px);
        opacity: 0.4;
        pointer-events: none;
        user-select: none;
    }
    .paywall-badge {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #000000;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 15px;
    }
    /* Input Fields Accent */
    input, select, textarea {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border: 1px solid #4B5563 !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 2. SAAS MULTI-TENANT CONFIGURATION & PERMISSIONS MATRIX
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
    },
    "starter_accountant": {
        "firm_name": "ANAND & ASSOCIATES TAX CONSULTANTS",
        "pass": "anandtax",
        "tier": "🟢 Starter Solo Tier",
        "managing_head": "Anand Kumar, Tax Practitioner",
        "allowed_modules": [1, 2] 
    }
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "tenant_id" not in st.session_state:
    st.session_state["tenant_id"] = None

# =========================================================================
# 3. SIDEBAR GATEWAY
# =========================================================================
st.sidebar.title("🔐 KSP SAAS ACCESS CONSOLE")

if not st.session_state["authenticated"]:
    st.sidebar.markdown("Enter credentials to enter environment:")
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
    st.sidebar.markdown(f"**📈 Tier:** {tenant_profile['tier']}")
    
    if st.sidebar.button("Disconnect Session Node", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["tenant_id"] = None
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ PLATFORM MODULES")

# SHOW ALL MODULES IN NAVIGATION (The Upsell Hook)
module_options_map = {
    "🚀 Module 1: Smart ITR Filing Engine": 1,
    "🏢 Module 2: Business Incorporation Strategy": 2,
    "🔵 Module 5: GST Command Center Core": 5,
    "📈 Module 6: Predictive Fractional CFO Model": 6,
    "📊 Module 3: Automated Valuation Modeler": 3,
    "🎤 Module 4: Strategic Pitch Deck Builder": 4
}
module_selection = st.sidebar.radio("Navigate Workspace", options=list(module_options_map.keys()), label_visibility="collapsed")
active_module_number = module_options_map[module_selection]
active_firm_name = tenant_profile["firm_name"]

# Check if the module is locked for the logged-in user
is_locked = active_module_number not in tenant_profile["allowed_modules"]

# =========================================================================
# 4. REUSEABLE WHITE-LABEL PDF REPORTLAB GENERATOR
# =========================================================================
def generate_base_pdf_layout(subtitle, firm_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T1', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#1E3A8A'), alignment=TA_CENTER)
    sub_style = ParagraphStyle('T2', fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#475569'), alignment=TA_CENTER)
    body_style = ParagraphStyle('B1', fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#1E293B'))
    story = [Paragraph(firm_name, title_style), Paragraph(subtitle, sub_style), Spacer(1, 15)]
    return buffer, doc, story, body_style

# =========================================================================
# 5. WORKSPACE RENDER DECK (WITH SMART PAYWALL FILTERS)
# =========================================================================

# INTERCEPT WITH PREMIUM PAYWALL INTERFACE IF FEATURE IS LOCKED
if is_locked:
    st.title(f"💼 {active_firm_name}")
    st.markdown(f"## {module_selection}")
    st.markdown("---")
    
    # Elegant Paywall UI Overlay
    with st.container(border=True):
        st.markdown("<span class='paywall-badge'>🔒 PREMIUM MODULE LOCKED</span>", unsafe_allow_html=True)
        st.markdown(f"### Upgrade Your Subscription to Access the Full Strategy Suite")
        st.markdown(
            "Your current plan does not include access to advanced financial intelligence features. "
            "Unlock this workspace module instantly to scale your accounting firm's portfolio value."
        )
        col_pay1, col_pay2 = st.columns([1, 3])
        with col_pay1:
            st.button("⚡ Upgrade License Instantly", type="primary", use_container_width=True)
            
    # Display the blurred preview of the underlying layout to incentivize conversion
    st.markdown("<div class='locked-feature'>", unsafe_allow_html=True)

# --- MODULE 1: SMART ITR FILING ENGINE ---
if active_module_number == 1:
    st.title(f"💼 {active_firm_name}")
    st.subheader("🚀 High-Value Smart ITR Filing Engine")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1: p_file = st.file_uploader("Upload Bank Records (PDF/CSV)")
    with col2: c_file = st.file_uploader("Upload AIS Document Profile")
    if p_file and c_file:
        st.success("✅ Dynamic Data Merging Pipeline Completed.")

# --- MODULE 2: BUSINESS INCORPORATION STRATEGY ---
elif active_module_number == 2:
    st.title(f"🏢 {active_firm_name}")
    st.subheader("Entity Optimization Workspace & Capitalization Modeler")
    st.markdown("---")
    st.text_input("Enterprise Name Option:", value="Gatty Pet Foods")
    st.selectbox("Structure Model Blueprint:", ["OPC", "LLP", "Pvt Ltd"])

# --- MODULE 5: GST COMMAND CENTER CORE ---
elif active_module_number == 5:
    st.title(f"🔵 {active_firm_name}")
    st.subheader("GST Command Center Core & Cross-Portal Audit Reconciliation")
    st.markdown("---")
    st.info("Drop sales ledgers against inward auto-drafted GSTR-2B datasets to reconcile mismatch indicators.")

# --- MODULE 6: PREDICTIVE FRACTIONAL CFO MODEL ---
elif active_module_number == 6:
    st.title(f"📈 {active_firm_name}")
    st.subheader("Predictive Fractional CFO Growth Strategy & Runway Modeler")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        cfo_burn = st.number_input("Monthly Operating Fixed Costs (INR):", min_value=1000, value=50000)
        cfo_rev = st.number_input("Monthly Inward Gross Revenue (INR):", min_value=1000, value=120000)
    with col2:
        # PREMIUM CHART ADDITION: Interactive Data Frame Area Visual
        st.markdown("**Projected Working Capital Runway Path (Next 6 Months)**")
        months = ["June", "July", "Aug", "Sept", "Oct", "Nov"]
        runway_projection = [(cfo_rev - cfo_burn) * i for i in range(1, 7)]
        chart_data = pd.DataFrame({"Net Reserve Cumulative Structure": runway_projection}, index=months)
        st.area_chart(chart_data, color="#3B82F6")

# --- MODULE 3: AUTOMATED VALUATION MODELER ---
elif active_module_number == 3:
    st.title(f"📊 {active_firm_name}")
    st.subheader("Automated Multi-Method Valuation Modeler Core")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        pat_val = st.number_input("Current Annual Net Profit / PAT (INR):", value=600000)
        sector = st.selectbox("Industry Classification:", ["Technology/SaaS", "D2C Brands", "Manufacturing"])
    with col2:
        growth_idx = st.slider("Validated Forward Growth Factor (%)", 0, 100, 25)
        
    mult = {"Technology/SaaS": 15, "D2C Brands": 8, "Manufacturing": 6}[sector]
    final_val = pat_val * mult * (1 + (growth_idx / 100))
    
    # Premium Interactive Visual Bar Chart
    st.markdown("### Strategic Valuation Analysis Spectrum")
    val_df = pd.DataFrame({
        "Valuation Model Approach": ["Asset Base Floor", "Sector Earnings Multiple", "Premium Valuation Target Model"],
        "Value (INR)": [pat_val * 2, final_val * 0.85, final_val]
    })
    st.bar_chart(val_df, x="Valuation Model Approach", y="Value (INR)", color="#F59E0B")
    
    if st.button("Generate Dynamic Valuation Report"):
        buf, doc, story, body = generate_base_pdf_layout("Automated Corporate Capital Valuation Summary", active_firm_name)
        story.append(Paragraph(f"<b>Assigned Sector Multiple Factor:</b> {mult}x", body))
        story.append(Paragraph(f"<b>Estimated Intrinsic Value Target:</b> INR {final_val:,.2f}", body))
        doc.build(story)
        st.download_button("📥 Download Branded Valuation Certificate", data=buf.getvalue(), file_name="Valuation_Certificate.pdf")

# --- MODULE 4: STRATEGIC PITCH DECK BUILDER ---
elif active_module_number == 4:
    st.title(f"🎤 {active_firm_name}")
    st.subheader("Strategic Venture Pitch Deck Outline Content Architect")
    st.markdown("---")
    st.text_area("Market Disruption Problem Statement:")
    st.number_input("Target Capital Funding Ask (INR):", value=5000000)

# Close blurring container wrapper safely if module is locked
if is_locked:
    st.markdown("</div>", unsafe_allow_html=True)