KSP CONSOLE PLATFORM — TaxSaaS B2B Engine
Kulkarni Strategic Partners | AY 2026-27
Production-Grade | Multi-Module | Login Protected
"""

import os, io, re, json, time
import pandas as pd
import numpy as np
import streamlit as st
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="KSP Console Platform",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — Dark Professional Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0D1117;
    color: #E2E8F0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #161B22 !important;
    border-right: 1px solid #30363D;
}
section[data-testid="stSidebar"] * { color: #C9D1D9 !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 0.85rem; }

/* Main area */
.main .block-container { padding-top: 1.5rem; }

/* Cards */
.ksp-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.ksp-card-accent { border-left: 3px solid #58A6FF; }
.ksp-card-success { border-left: 3px solid #3FB950; }
.ksp-card-warning { border-left: 3px solid #D29922; }
.ksp-card-danger { border-left: 3px solid #F85149; }

/* Metric overrides */
[data-testid="metric-container"] {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 0.75rem 1rem;
}
[data-testid="metric-container"] label { color: #8B949E !important; font-size: 0.75rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #58A6FF !important; font-family: 'IBM Plex Mono' !important; font-size: 1.4rem !important; }

/* Buttons */
.stButton > button {
    background: #238636 !important;
    color: #FFFFFF !important;
    border: 1px solid #2EA043 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Sans' !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    padding: 0.5rem 1.25rem !important;
    width: 100%;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #2EA043 !important;
    box-shadow: 0 0 10px rgba(46,160,67,0.4) !important;
}

.login-btn > button { background: #1F6FEB !important; border: 1px solid #388BFD !important; }
.login-btn > button:hover { background: #388BFD !important; box-shadow: 0 0 10px rgba(56,139,253,0.4) !important; }

/* Text inputs */
.stTextInput > div > div > input,
.stTextArea textarea, .stNumberInput input {
    background: #0D1117 !important;
    border: 1px solid #30363D !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
    font-family: 'IBM Plex Mono' !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #58A6FF !important;
    box-shadow: 0 0 0 2px rgba(88,166,255,0.15) !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background: #0D1117 !important;
    border: 1px solid #30363D !important;
    color: #E2E8F0 !important;
}

/* Divider */
hr { border-color: #30363D !important; margin: 1rem 0; }
.stJson { background: #0D1117 !important; border: 1px solid #30363D !important; border-radius: 6px; }

[data-testid="stFileUploader"] {
    background: #161B22 !important;
    border: 1px dashed #30363D !important;
    border-radius: 8px !important;
}

.stSpinner > div { border-top-color: #58A6FF !important; }
.stSuccess { background: #0D2818 !important; border: 1px solid #3FB950 !important; border-radius: 6px !important; }
.stWarning { background: #1C1700 !important; border: 1px solid #D29922 !important; border-radius: 6px !important; }
.stError   { background: #2D0F0E !important; border: 1px solid #F85149 !important; border-radius: 6px !important; }

.stTabs [data-baseweb="tab-list"] { background: #161B22 !important; border-bottom: 1px solid #30363D; gap: 0; }
.stTabs [data-baseweb="tab"] { color: #8B949E !important; background: transparent !important; border-radius: 0 !important; font-size: 0.85rem !important; padding: 0.5rem 1rem !important; }
.stTabs [aria-selected="true"] { color: #58A6FF !important; border-bottom: 2px solid #58A6FF !important; }

/* Header brand bar */
.brand-bar {
    display: flex; align-items: center; gap: 12px;
    padding: 0.6rem 0 0.6rem 0;
    border-bottom: 1px solid #30363D;
    margin-bottom: 1.5rem;
}
.brand-bar .logo { font-size: 1.5rem; }
.brand-bar .title { font-family: 'IBM Plex Mono'; font-size: 1.1rem; font-weight: 600; color: #58A6FF; letter-spacing: 0.05em; }
.brand-bar .subtitle { font-size: 0.75rem; color: #8B949E; margin-top: 2px; }
.status-badge {
    margin-left: auto; background: #0D2818; border: 1px solid #3FB950;
    color: #3FB950; border-radius: 12px; padding: 2px 10px; font-size: 0.72rem; font-family: 'IBM Plex Mono';
}

.login-container {
    max-width: 450px; margin: 5rem auto;
    background: #161B22; border: 1px solid #30363D;
    border-radius: 12px; padding: 2.5rem;
}
.login-logo { text-align: center; font-size: 3rem; margin-bottom: 0.5rem; }
.login-title { text-align: center; font-family: 'IBM Plex Mono'; font-size: 1.2rem; color: #58A6FF; font-weight: 600; }
.login-sub { text-align: center; font-size: 0.8rem; color: #8B949E; margin-bottom: 2rem; }

.info-box {
    background: #0C2A4A; border: 1px solid #1F6FEB;
    border-radius: 8px; padding: 1rem 1.25rem;
    font-size: 0.85rem; color: #58A6FF; margin-bottom: 1rem;
}
.section-header {
    font-family: 'IBM Plex Mono'; font-size: 0.7rem; font-weight: 600;
    color: #8B949E; letter-spacing: 0.12em; text-transform: uppercase;
    margin: 1.25rem 0 0.6rem 0; border-bottom: 1px solid #21262D; padding-bottom: 4px;
}

[data-testid="stDownloadButton"] > button {
    background: #161B22 !important;
    border: 1px solid #58A6FF !important;
    color: #58A6FF !important;
    width: auto !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #0C2A4A !important; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  B2B CREDENTIALS STORE
# ─────────────────────────────────────────────
B2B_USERS = {
    "admin"          : ("KSP@2026#Admin",  "Kulkarni Strategic Partners","ENTERPRISE", "all"),
    "ca_shashank"    : ("Shashank@KSP1",   "Shashank Kulkarni & Associates","PRO",    "all"),
    "firm_abc"       : ("FirmABC@2026",    "ABC Tax Consultants",         "STANDARD", ["itr"]),
    "demo_user"      : ("Demo@1234",       "Demo Firm (Trial)",           "TRIAL",    ["itr"]),
}

def authenticate(username, password):
    user = B2B_USERS.get(username.lower().strip())
    if user and user[0] == password:
        return {"username": username, "firm": user[1], "plan": user[2], "modules": user[3]}
    return None

def has_module_access(modules_allowed, module_key):
    if modules_allowed == "all":
        return True
    return module_key in modules_allowed

# ─────────────────────────────────────────────
#  CORE FINTECH LOGIC & TAX ENGINE SUBSYSTEM
# ─────────────────────────────────────────────
def clean_numerical_value(val_str):
    if not val_str: return 0.0
    sanitized = val_str.strip().replace('"', '').replace("'", "").replace(" ", "").replace(',', '')
    if 'cr' in sanitized.lower(): sanitized = sanitized.lower().replace('cr', '').strip()
    elif 'dr' in sanitized.lower(): sanitized = sanitized.lower().replace('dr', '').strip()
    try:
        return float(sanitized)
    except ValueError:
        nums = re.findall(r'[-+]?\d*\.\d+|\d+', sanitized)
        return float(nums[0]) if nums else 0.0

def process_pdf_statement_fixed(file_bytes):
    pdf_file = io.BytesIO(file_bytes)
    reader = PdfReader(pdf_file)
    total_turnover = 0.0
    row_count = 0
    for page in reader.pages:
        text = page.extract_text()
        if not text: continue
        for line in text.split('\n'):
            line_str = line.strip()
            if any(k in line_str.lower() for k in ["statement of account", "clear balance", "drawing power"]): continue
            if any(m in line_str.lower() for m in ["transfer", "upi", "cr", "neft", "rtgs", "imdb"]):
                tokens = line_str.split()
                candidate_amounts = [t for t in tokens if re.match(r'^\d+[\d,]*(\.\d{2})?$', t.replace(',', ''))]
                if len(candidate_amounts) >= 2 and ("cr" in line_str.lower() or "upi/cr" in line_str.lower()):
                    total_turnover += clean_numerical_value(candidate_amounts[-2])
                    row_count += 1
                elif len(candidate_amounts) == 1 and ("cr" in line_str.lower() or "deposit" in line_str.lower()):
                    total_turnover += clean_numerical_value(candidate_amounts[0])
                    row_count += 1
    return total_turnover, row_count

def calculate_tax_ay_2026_27(income_details):
    stcg = income_details.get("stcg", 0.0)
    ltcg = income_details.get("ltcg", 0.0)
    other_inc = income_details.get("other_income", 0.0)
    deductions = income_details.get("deductions", 0.0)

    # FINANCE ACT AY 2026-27 SPECIFIC SPECIAL RATES
    tax_stcg = stcg * 0.20  # Section 111A updated to 20%
    tax_ltcg = max(0.0, (ltcg - 125000) * 0.125)  # Section 112A threshold: ₹1.25L, rate: 12.5%