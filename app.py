"""
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
.ksp-card-accent {
    border-left: 3px solid #58A6FF;
}
.ksp-card-success {
    border-left: 3px solid #3FB950;
}
.ksp-card-warning {
    border-left: 3px solid #D29922;
}
.ksp-card-danger {
    border-left: 3px solid #F85149;
}

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
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #2EA043 !important;
    box-shadow: 0 0 10px rgba(46,160,67,0.4) !important;
}

/* Login button special */
.login-btn > button {
    background: #1F6FEB !important;
    border: 1px solid #388BFD !important;
}
.login-btn > button:hover { background: #388BFD !important; box-shadow: 0 0 10px rgba(56,139,253,0.4) !important; }

/* Text inputs */
.stTextInput > div > div > input,
.stTextArea textarea {
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

/* JSON display */
.stJson { background: #0D1117 !important; border: 1px solid #30363D !important; border-radius: 6px; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #161B22 !important;
    border: 1px dashed #30363D !important;
    border-radius: 8px !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #58A6FF !important; }

/* Success/Warning/Error boxes */
.stSuccess { background: #0D2818 !important; border: 1px solid #3FB950 !important; border-radius: 6px !important; }
.stWarning { background: #1C1700 !important; border: 1px solid #D29922 !important; border-radius: 6px !important; }
.stError   { background: #2D0F0E !important; border: 1px solid #F85149 !important; border-radius: 6px !important; }

/* Tabs */
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

/* Module card in sidebar */
.module-active { color: #58A6FF !important; font-weight: 600 !important; }

/* Login page */
.login-container {
    max-width: 420px; margin: 6rem auto;
    background: #161B22; border: 1px solid #30363D;
    border-radius: 12px; padding: 2.5rem;
}
.login-logo { text-align: center; font-size: 3rem; margin-bottom: 0.5rem; }
.login-title { text-align: center; font-family: 'IBM Plex Mono'; font-size: 1.2rem; color: #58A6FF; font-weight: 600; }
.login-sub { text-align: center; font-size: 0.8rem; color: #8B949E; margin-bottom: 2rem; }

/* Info box */
.info-box {
    background: #0C2A4A; border: 1px solid #1F6FEB;
    border-radius: 8px; padding: 1rem 1.25rem;
    font-size: 0.85rem; color: #58A6FF; margin-bottom: 1rem;
}

/* Section header */
.section-header {
    font-family: 'IBM Plex Mono'; font-size: 0.7rem; font-weight: 600;
    color: #8B949E; letter-spacing: 0.12em; text-transform: uppercase;
    margin: 1.25rem 0 0.6rem 0; border-bottom: 1px solid #21262D; padding-bottom: 4px;
}

/* Download button override */
[data-testid="stDownloadButton"] > button {
    background: #161B22 !important;
    border: 1px solid #58A6FF !important;
    color: #58A6FF !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #0C2A4A !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  B2B CREDENTIALS STORE
#  In production: replace with DB / env secrets
# ─────────────────────────────────────────────
B2B_USERS = {
    # username       : (password,          firm_name,                    plan,       modules_allowed)
    "admin"          : ("KSP@2026#Admin",  "Kulkarni Strategic Partners","ENTERPRISE", "all"),
    "ca_shashank"    : ("Shashank@KSP1",   "Shashank Kulkarni & Associates","PRO",    "all"),
    "firm_abc"       : ("FirmABC@2026",    "ABC Tax Consultants",         "STANDARD", ["itr","gst"]),
    "firm_xyz"       : ("XYZ@Filing1",     "XYZ Financial Services",      "PRO",      "all"),
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
#  SESSION STATE BOOTSTRAP
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "logged_in": False, "user": None,
        "active_module": "itr",
        "itr_pdf_bytes": None, "itr_pdf_filename": "",
        "gst_pdf_bytes": None,
        "last_itr_result": None,
        "last_gst_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────
def render_login():
    st.markdown("""
    <div class="login-container">
        <div class="login-logo">⚙️</div>
        <div class="login-title">KSP CONSOLE PLATFORM</div>
        <div class="login-sub">B2B Tax & Compliance SaaS · AY 2026-27<br/>Authorised Firm Access Only</div>
    </div>
    """, unsafe_allow_html=True)

    col_c = st.columns([1, 2, 1])[1]
    with col_c:
        uname = st.text_input("Username", placeholder="Enter your firm username", key="login_u")
        pwd   = st.text_input("Password", type="password", placeholder="Enter password", key="login_p")
        st.markdown("")

        login_col = st.container()
        with login_col:
            st.markdown('<div class="login-btn">', unsafe_allow_html=True)
            clicked = st.button("🔐  Authenticate & Enter Platform", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if clicked:
            result = authenticate(uname, pwd)
            if result:
                st.session_state.logged_in = True
                st.session_state.user = result
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Contact your KSP administrator.")

        st.markdown("""
        <div style="text-align:center; margin-top:1.5rem; font-size:0.75rem; color:#484F58;">
        🔒 Encrypted session · Authorised clients only<br/>
        Contact: admin@kspfiling.in for access
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TAX ENGINE (ITR MODULE — AY 2026-27)
# ─────────────────────────────────────────────
class RobustTaxEngine:
    def __init__(self, bank_file=None, ais_file=None, ledger_file=None):
        self.bank_file   = bank_file
        self.ais_file    = ais_file
        self.ledger_file = ledger_file

        self.gross_receipts          = 0.0
        self.presumptive_profit      = 0.0
        self.stcg_111a               = 0.0   # Listed equity / ETF STCG
        self.stcg_other              = 0.0   # Debt / other STCG (slab rate)
        self.ltcg_112a               = 0.0   # Listed equity LTCG (10% above 1.25L)
        self.ltcg_other              = 0.0   # Debt / other LTCG (20% with indexation)
        self.salary_income           = 0.0
        self.other_sources_income    = 0.0
        self.total_deductions        = 0.0   # Only relevant for OLD regime

        self.is_director_or_unlisted = False
        self.has_foreign_assets      = False
        self.has_agri_over_5k        = False

    # ── BANK PARSER ──────────────────────────
    def parse_bank_statement(self):
        if not self.bank_file:
            return
        try:
            ext = self.bank_file.name.lower()
            if ext.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.bank_file, engine='openpyxl')
                self._process_bank_df(df)
            elif ext.endswith('.csv'):
                df = pd.read_csv(self.bank_file)
                self._process_bank_df(df)
            elif ext.endswith('.pdf'):
                self._parse_bank_pdf()
        except Exception as e:
            st.error(f"Bank parsing error: {e}")

    def _parse_bank_pdf(self):
        pdf = PdfReader(self.bank_file)
        total = 0.0
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                line = line.strip()
                if any(k in line.upper() for k in ["(CR)", "CREDIT", "UPI", "NEFT", "RTGS", "IMPS", "SALARY"]):
                    if "DR" in line.upper() or "DEBIT" in line.upper():
                        continue
                    nums = re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b', line)
                    if nums:
                        try:
                            val = float(nums[-2].replace(",","")) if len(nums) >= 2 else float(nums[-1].replace(",",""))
                            total += val
                        except:
                            pass
        self.gross_receipts = round(total, 2)

    def _process_bank_df(self, df):
        df.columns = [str(c).strip().upper() for c in df.columns]
        cr_col   = next((c for c in df.columns if any(k in c for k in ['CREDIT','DEPOSIT','CR','INWARD'])), None)
        desc_col = next((c for c in df.columns if any(k in c for k in ['DESC','REMARK','NARRATION','PARTICULARS','DETAILS'])), None)
        if cr_col:
            df[cr_col] = pd.to_numeric(df[cr_col].astype(str).str.replace(",",""), errors='coerce').fillna(0)
            if desc_col:
                mask = df[desc_col].astype(str).str.contains('REVERSAL|ROLLBACK|REFUND|FAILED', case=False, na=False)
                self.gross_receipts = float(df[~mask][cr_col].sum())
            else:
                self.gross_receipts = float(df[cr_col].sum())

    # ── STOCK LEDGER PARSER ──────────────────
    def parse_stock_ledger(self):
        if not self.ledger_file:
            return
        try:
            ext = self.ledger_file.name.lower()
            if ext.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.ledger_file, engine='openpyxl')
                self._process_ledger_df(df)
            elif ext.endswith('.csv'):
                df = pd.read_csv(self.ledger_file)
                self._process_ledger_df(df)
            elif ext.endswith('.pdf'):
                self._parse_ledger_pdf()
        except Exception as e:
            st.error(f"Ledger parsing error: {e}")

    def _parse_ledger_pdf(self):
        pdf = PdfReader(self.ledger_file)
        full = "".join(p.extract_text() or "" for p in pdf.pages)
        patterns = {
            'stcg_111a': r'(?:STCG|SHORT[\s\-]TERM\s+(?:EQUITY|LISTED|111A))[^\d]*(\d[\d,]*\.?\d*)',
            'ltcg_112a': r'(?:LTCG|LONG[\s\-]TERM\s+(?:EQUITY|LISTED|112A))[^\d]*(\d[\d,]*\.?\d*)',
            'stcg_other': r'(?:STCG[\s\-]+OTHER|SHORT[\s\-]TERM\s+DEBT)[^\d]*(\d[\d,]*\.?\d*)',
            'ltcg_other': r'(?:LTCG[\s\-]+OTHER|LONG[\s\-]TERM\s+DEBT)[^\d]*(\d[\d,]*\.?\d*)',
        }
        for field, pat in patterns.items():
            m = re.search(pat, full, re.IGNORECASE)
            if m:
                setattr(self, field, float(m.group(1).replace(",","")))

    def _process_ledger_df(self, df):
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapping = {
            'stcg_111a': ['STCG','SHORT TERM EQUITY','111A','SHORT-TERM'],
            'ltcg_112a': ['LTCG','LONG TERM EQUITY','112A','LONG-TERM'],
            'stcg_other': ['STCG OTHER','SHORT TERM DEBT','ST_OTHER'],
            'ltcg_other': ['LTCG OTHER','LONG TERM DEBT','LT_OTHER'],
        }
        for field, keys in mapping.items():
            col = next((c for c in df.columns if any(k in c for k in keys)), None)
            if col:
                setattr(self, field, float(pd.to_numeric(df[col].astype(str).str.replace(",",""), errors='coerce').sum()))

    # ── CORE TAX COMPUTE — AY 2026-27 CORRECTED ──
    def compute(self, route, regime="NEW"):
        has_business = self.gross_receipts > 0
        has_cg = any([self.stcg_111a, self.stcg_other, self.ltcg_112a, self.ltcg_other])

        # ITR FORM SELECTION
        if self.has_foreign_assets or self.is_director_or_unlisted:
            itr_form = "ITR-3"
        elif has_cg:
            itr_form = "ITR-3" if has_business else "ITR-2"
        elif has_business:
            if "44AD" in route and self.gross_receipts <= 30_000_000:
                itr_form = "ITR-4"
                self.presumptive_profit = round(self.gross_receipts * 0.06, 2)
            elif "44ADA" in route and self.gross_receipts <= 7_500_000:
                itr_form = "ITR-4"
                self.presumptive_profit = round(self.gross_receipts * 0.50, 2)
            else:
                itr_form = "ITR-3"
        else:
            if self.has_agri_over_5k or (self.salary_income + self.other_sources_income > 5_000_000):
                itr_form = "ITR-2"
            else:
                itr_form = "ITR-1"

        # INCOME AGGREGATION
        gross_total = (
            self.salary_income + self.presumptive_profit +
            self.stcg_111a + self.stcg_other +
            self.ltcg_112a + self.ltcg_other +
            self.other_sources_income
        )

        if regime == "NEW":
            net_taxable = max(0.0, gross_total)   # No Chapter VIA deductions in new regime
            standard_deduction = min(75_000, self.salary_income) if self.salary_income > 0 else 0
            net_taxable = max(0.0, net_taxable - standard_deduction)
        else:
            net_taxable = max(0.0, gross_total - self.total_deductions)
            standard_deduction = min(50_000, self.salary_income) if self.salary_income > 0 else 0
            net_taxable = max(0.0, net_taxable - standard_deduction)

        # SLAB INCOME (exclude special rate CG)
        special_cg = self.stcg_111a + self.stcg_other + self.ltcg_112a + self.ltcg_other
        slab_income = max(0.0, net_taxable - special_cg)

        # SLAB TAX — AY 2026-27 NEW REGIME (Budget 2025 Updated Slabs)
        raw_slab_tax = 0.0
        if regime == "NEW":
            slabs = [(400000,0),(800000,0.05),(1200000,0.10),(1600000,0.15),(2000000,0.20),(float('inf'),0.30)]
            prev, running = 0, 0.0
            for limit, rate in slabs:
                if slab_income > prev:
                    taxable_chunk = min(slab_income, limit) - prev
                    running += taxable_chunk * rate
                    prev = limit
                else:
                    break
            raw_slab_tax = running
        else:
            # OLD REGIME
            if slab_income > 1_000_000:
                raw_slab_tax = (slab_income - 1_000_000)*0.30 + 112500
            elif slab_income > 500_000:
                raw_slab_tax = (slab_income - 500_000)*0.20 + 12500
            elif slab_income > 250_000:
                raw_slab_tax = (slab_income - 250_000)*0.05

        # CAPITAL GAINS TAX — POST BUDGET 2024 CORRECTED RATES
        # Sec 111A STCG on listed equity: 20% (was 15%, changed Finance Act 2024)
        stcg_111a_tax  = self.stcg_111a * 0.20
        # STCG other (debt, etc.): slab rate — already counted above via slab_income inclusion
        stcg_other_tax = 0.0  # Included in slab income above

        # Sec 112A LTCG listed equity: 12.5% above ₹1.25L exemption (Finance Act 2024)
        ltcg_112a_exempt = 125_000
        ltcg_112a_tax = max(0.0, (self.ltcg_112a - ltcg_112a_exempt) * 0.125) if self.ltcg_112a > ltcg_112a_exempt else 0.0

        # LTCG other (debt): 12.5% no indexation (Finance Act 2024 change)
        ltcg_other_tax = self.ltcg_other * 0.125

        total_pre_rebate = raw_slab_tax + stcg_111a_tax + stcg_other_tax + ltcg_112a_tax + ltcg_other_tax

        # SECTION 87A REBATE — AY 2026-27
        # New Regime: rebate up to ₹25,000 if net taxable income ≤ ₹12,00,000
        # Old Regime: rebate up to ₹12,500 if net taxable income ≤ ₹5,00,000
        # NOTE: 87A NOT available on STCG 111A/112A special rate income
        rebate_eligible_tax = raw_slab_tax  # Only slab tax qualifies
        if regime == "NEW":
            rebate = min(25_000, rebate_eligible_tax) if net_taxable <= 1_200_000 else 0.0
        else:
            rebate = min(12_500, rebate_eligible_tax) if net_taxable <= 500_000 else 0.0

        net_tax = max(0.0, total_pre_rebate - rebate)

        # SURCHARGE (simplified — no marginal relief here)
        surcharge = 0.0
        if net_taxable > 5_000_000:
            surcharge_rate = 0.10 if net_taxable <= 10_000_000 else (0.15 if net_taxable <= 20_000_000 else 0.25)
            surcharge = net_tax * surcharge_rate

        # CESS: 4% on (tax + surcharge)
        cess = (net_tax + surcharge) * 0.04
        final_tax = round(net_tax + surcharge + cess, 2)

        # AUDIT TRIGGER CHECK (44AB)
        audit_required = (
            (has_business and self.gross_receipts > 10_000_000) or
            (has_business and "44AD" in route and self.presumptive_profit < self.gross_receipts * 0.06) or
            ("44ADA" in route and self.presumptive_profit < self.gross_receipts * 0.50)
        )

        return {
            "assigned_form": itr_form,
            "regime": regime,
            "audit_required": audit_required,
            "metrics": {
                "Gross Receipts / Turnover": round(self.gross_receipts, 2),
                "Presumptive Profit (Sec 44AD/44ADA)": round(self.presumptive_profit, 2),
                "Salary Income": round(self.salary_income, 2),
                "Standard Deduction Applied": round(standard_deduction, 2),
                "STCG — Sec 111A (Listed Equity, 20%)": round(self.stcg_111a, 2),
                "STCG — Other (Slab Rate)": round(self.stcg_other, 2),
                "LTCG — Sec 112A (Listed Equity, 12.5%)": round(self.ltcg_112a, 2),
                "LTCG — Other (12.5%)": round(self.ltcg_other, 2),
                "Other Source Income": round(self.other_sources_income, 2),
                "Gross Total Income (GTI)": round(gross_total, 2),
                "Net Taxable Income": round(net_taxable, 2),
            },
            "tax_breakdown": {
                "Slab Tax (Base)": round(raw_slab_tax, 2),
                "STCG Tax — 111A @ 20%": round(stcg_111a_tax, 2),
                "LTCG Tax — 112A @ 12.5%": round(ltcg_112a_tax, 2),
                "LTCG Other @ 12.5%": round(ltcg_other_tax, 2),
                "Total Pre-Rebate Tax": round(total_pre_rebate, 2),
                "Section 87A Rebate": round(rebate, 2),
                "Surcharge": round(surcharge, 2),
                "Health & Education Cess (4%)": round(cess, 2),
                "NET TAX PAYABLE": round(final_tax, 2),
            },
            "compliance_flags": {
                "Sec 44AB Audit Required": "YES ⚠️" if audit_required else "NO ✅",
                "Foreign Assets Disclosure": "YES — Schedule FA Required" if self.has_foreign_assets else "NOT APPLICABLE",
                "Directorship / Unlisted Shares": "YES — ITR-3 Mandatory" if self.is_director_or_unlisted else "NOT APPLICABLE",
                "Agricultural Income": "YES — Partial Integration Required" if self.has_agri_over_5k else "NOT APPLICABLE",
            }
        }

# ─────────────────────────────────────────────
#  GST MODULE ENGINE
# ─────────────────────────────────────────────
class GSTEngine:
    def __init__(self):
        self.turnover        = 0.0
        self.taxable_supply  = 0.0
        self.exempt_supply   = 0.0
        self.export_supply   = 0.0
        self.itc_claimed     = 0.0
        self.tax_paid_cash   = 0.0
        self.state           = "Telangana"

    def compute_gst_liability(self, rate_structure: dict):
        """
        rate_structure: {"0%": amt, "5%": amt, "12%": amt, "18%": amt, "28%": amt}
        """
        gross_output_tax = 0.0
        breakdown = {}
        for rate_str, supply_val in rate_structure.items():
            rate = float(rate_str.replace("%","")) / 100
            tax = supply_val * rate
            igst = tax  # Simplified — inter-state assumption
            cgst = sgst = tax / 2  # Intra-state
            gross_output_tax += tax
            breakdown[rate_str] = {
                "Taxable Value": round(supply_val, 2),
                "Output Tax": round(tax, 2),
                "CGST": round(cgst, 2),
                "SGST": round(sgst, 2),
            }

        net_gst_payable = max(0.0, gross_output_tax - self.itc_claimed)
        cash_liability  = max(0.0, net_gst_payable - self.tax_paid_cash)
        annual_turnover = sum(rate_structure.values()) + self.exempt_supply + self.export_supply

        # Registration threshold check
        reg_threshold  = 2_000_000  # ₹20L (regular)
        comp_threshold = 15_000_000  # ₹1.5Cr for composition
        reg_required   = annual_turnover >= reg_threshold
        comp_eligible  = annual_turnover <= comp_threshold and self.exempt_supply == 0

        # GSTR filing calendar
        gstr_filing = {
            "GSTR-1 (Outward Supplies)": "11th of following month / Quarterly (QRMP)",
            "GSTR-3B (Summary Return)": "20th of following month",
            "GSTR-9 (Annual Return)": "31st December (if turnover > ₹2Cr)",
            "GSTR-9C (Reconciliation)": "31st December (if turnover > ₹5Cr)",
        }

        return {
            "annual_turnover": round(annual_turnover, 2),
            "registration_required": reg_required,
            "composition_eligible": comp_eligible,
            "rate_breakdown": breakdown,
            "summary": {
                "Gross Output Tax": round(gross_output_tax, 2),
                "ITC Available": round(self.itc_claimed, 2),
                "Net GST Payable": round(net_gst_payable, 2),
                "Cash Ledger Requirement": round(cash_liability, 2),
                "Export (Zero-Rated) Supply": round(self.export_supply, 2),
                "Exempt Supply": round(self.exempt_supply, 2),
            },
            "gstr_calendar": gstr_filing,
            "compliance_flags": {
                "GST Registration": "REQUIRED ✅" if reg_required else "BELOW THRESHOLD",
                "Composition Scheme Eligible": "YES" if comp_eligible else "NO",
                "LUT Required for Export": "YES — File LUT before export" if self.export_supply > 0 else "NOT APPLICABLE",
                "Reverse Charge Applicable": "CHECK — Verify RCM applicability",
            }
        }

# ─────────────────────────────────────────────
#  PDF GENERATORS
# ─────────────────────────────────────────────
def generate_itr_pdf(name, pan, firm, result):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story  = []

    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=15,
                              textColor=colors.HexColor("#1A365D"), spaceAfter=6)
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=11,
                              textColor=colors.HexColor("#2C5282"), spaceBefore=12, spaceAfter=4)
    body_s  = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=13)
    bold_s  = ParagraphStyle('Bo', parent=body_s, fontName='Helvetica-Bold')
    small_s = ParagraphStyle('S', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#666"))

    # Header
    story.append(Paragraph("KSP CONSOLE PLATFORM — Compliance Report", title_s))
    story.append(Paragraph(f"Kulkarni Strategic Partners · {firm}", body_s))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=10))

    meta = [
        [Paragraph(f"<b>Assessee:</b> {name}", body_s), Paragraph(f"<b>AY:</b> 2026-27 (FY 2025-26)", body_s)],
        [Paragraph(f"<b>PAN:</b> {pan}", body_s), Paragraph(f"<b>ITR Form:</b> {result['assigned_form']}", body_s)],
        [Paragraph(f"<b>Regime:</b> {result['regime']} REGIME (Sec 115BAC)", body_s),
         Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%d %b %Y %H:%M')}", body_s)],
    ]
    t = Table(meta, colWidths=[265, 265])
    t.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
        ('PADDING',(0,0),(-1,-1),5),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#EDF2F7")),
    ]))
    story.append(t); story.append(Spacer(1,12))

    # Income Metrics
    story.append(Paragraph("I. Income Ingestion Summary", h2_s))
    rows = [[Paragraph("<b>Field</b>",body_s), Paragraph("<b>Amount (INR)</b>",body_s)]]
    for k,v in result["metrics"].items():
        rows.append([Paragraph(k,body_s), Paragraph(f"₹ {v:,.2f}",body_s)])
    t2 = Table(rows, colWidths=[370,160])
    t2.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#EDF2F7")),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
        ('PADDING',(0,0),(-1,-1),4),
    ]))
    story.append(t2); story.append(Spacer(1,12))

    # Tax Computation
    story.append(Paragraph("II. Tax Computation Matrix", h2_s))
    rows2 = [[Paragraph("<b>Component</b>",body_s), Paragraph("<b>Amount (INR)</b>",body_s)]]
    for k,v in result["tax_breakdown"].items():
        style = bold_s if "NET TAX" in k else body_s
        rows2.append([Paragraph(f"<b>{k}</b>" if "NET TAX" in k else k, style), Paragraph(f"₹ {v:,.2f}", style)])
    t3 = Table(rows2, colWidths=[370,160])
    t3.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#EDF2F7")),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
        ('PADDING',(0,0),(-1,-1),4),
        ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor("#E2E8F0")),
    ]))
    story.append(t3); story.append(Spacer(1,12))

    # Compliance Flags
    story.append(Paragraph("III. Compliance Flags & Regulatory Triggers", h2_s))
    for k,v in result["compliance_flags"].items():
        story.append(Paragraph(f"<b>{k}:</b> {v}", body_s))
        story.append(Spacer(1,3))
    story.append(Spacer(1,10))

    # E-Filing Steps
    story.append(Paragraph("IV. Step-by-Step E-Filing Blueprint", h2_s))
    net_tax = result['tax_breakdown']['NET TAX PAYABLE']
    rebate  = result['tax_breakdown']['Section 87A Rebate']
    steps = [
        f"<b>Step 1 — Form Selection:</b> Login to incometax.gov.in → File ITR → AY 2026-27 → Select <b>{result['assigned_form']}</b>.",
        f"<b>Step 2 — Regime:</b> Select <b>{result['regime']} REGIME</b> under Section 115BAC. Confirm regime before proceeding.",
        f"<b>Step 3 — Schedule BP:</b> Enter Gross Receipts: <b>₹ {result['metrics']['Gross Receipts / Turnover']:,.2f}</b> | Presumptive Profit: <b>₹ {result['metrics']['Presumptive Profit (Sec 44AD/44ADA)']:,.2f}</b>",
        f"<b>Step 4 — Schedule CG:</b> Sec 111A STCG: <b>₹ {result['metrics']['STCG — Sec 111A (Listed Equity, 20%)']:,.2f}</b> @ 20% | Sec 112A LTCG: <b>₹ {result['metrics']['LTCG — Sec 112A (Listed Equity, 12.5%)']:,.2f}</b> @ 12.5%",
        f"<b>Step 5 — Part B-TTI:</b> Verify Sec 87A Rebate: <b>₹ {rebate:,.2f}</b> | Final Net Tax: <b>₹ {net_tax:,.2f}</b>",
        "<b>Step 6 — Pre-Submit:</b> Cross-verify with Form 26AS and AIS. Ensure all TDS credits are matched.",
        "<b>Step 7 — E-Verify:</b> Submit → Preview → E-Verify via Aadhaar OTP or Net Banking within 30 days.",
    ]
    for s in steps:
        story.append(Paragraph(s, body_s))
        story.append(Spacer(1,4))

    story.append(Spacer(1,15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0")))
    story.append(Paragraph("Disclaimer: This report is generated by KSP Console Platform for professional reference only. Verify all figures with source documents before filing.", small_s))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def generate_gst_pdf(name, gstin, firm, result):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story  = []

    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor("#1A365D"), spaceAfter=6)
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor("#2C5282"), spaceBefore=12, spaceAfter=4)
    body_s  = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=13)

    story.append(Paragraph("KSP CONSOLE PLATFORM — GST Compliance Report", title_s))
    story.append(Paragraph(f"Kulkarni Strategic Partners · {firm}", body_s))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=10))

    meta = [
        [Paragraph(f"<b>Business Name:</b> {name}", body_s), Paragraph(f"<b>GSTIN:</b> {gstin}", body_s)],
        [Paragraph(f"<b>Annual Turnover:</b> ₹ {result['annual_turnover']:,.2f}", body_s),
         Paragraph(f"<b>Registration:</b> {result['compliance_flags']['GST Registration']}", body_s)],
    ]
    t = Table(meta, colWidths=[265, 265])
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
                            ('PADDING',(0,0),(-1,-1),5),
                            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#EDF2F7"))]))
    story.append(t); story.append(Spacer(1,12))

    story.append(Paragraph("I. GST Liability Summary", h2_s))
    rows = [[Paragraph("<b>Component</b>",body_s), Paragraph("<b>Amount (INR)</b>",body_s)]]
    for k,v in result["summary"].items():
        rows.append([Paragraph(k,body_s), Paragraph(f"₹ {v:,.2f}",body_s)])
    t2 = Table(rows, colWidths=[370,160])
    t2.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#EDF2F7")),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
        ('PADDING',(0,0),(-1,-1),4),
    ]))
    story.append(t2); story.append(Spacer(1,10))

    story.append(Paragraph("II. GSTR Filing Calendar", h2_s))
    for form, due in result["gstr_calendar"].items():
        story.append(Paragraph(f"<b>{form}:</b> {due}", body_s))
        story.append(Spacer(1,3))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

# ─────────────────────────────────────────────
#  MODULE: ITR FILING ENGINE
# ─────────────────────────────────────────────
def render_itr_module(user):
    st.markdown('<div class="section-header">Active Client Configuration</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Client Legal Name", placeholder="e.g. Dixith Chakravarthula")
        pan  = st.text_input("PAN Number", placeholder="ABCDE1234F", max_chars=10)
    with c2:
        salary   = st.number_input("Salary Income (₹)", min_value=0.0, step=1000.0, format="%.2f")
        other_inc= st.number_input("Other Sources Income (₹)", min_value=0.0, step=1000.0, format="%.2f")
    with c3:
        deductions = st.number_input("Chapter VIA Deductions (₹) [Old Regime]", min_value=0.0, step=1000.0, format="%.2f")
        regime     = st.selectbox("Tax Regime", ["NEW (Sec 115BAC)", "OLD (Regular)"])

    st.markdown('<div class="section-header">Business Route & Flags</div>', unsafe_allow_html=True)
    cf1, cf2, cf3 = st.columns(3)
    with cf1:
        route = st.radio("Filing Route:", [
            "Small Business / Trade (Sec 44AD)",
            "Professional / Freelance (Sec 44ADA)",
            "None (Salaried / Passive Only)"
        ])
    with cf2:
        d_flag = st.checkbox("Director / Holds Unlisted Equity")
        f_flag = st.checkbox("Foreign Assets / Foreign Accounts")
        a_flag = st.checkbox("Agricultural Income > ₹5,000")
    with cf3:
        profile_model = st.selectbox("Client Profile Model", [
            "Salaried Professional",
            "Traditional Professional / Priest (Dakshina & Pooja Inflows)",
            "Freelancer / Consultant",
            "Small Retailer / Trader",
            "Investor (Equity & MF)",
            "HUF",
            "NRI / Foreign Income",
        ])

    st.markdown('<div class="section-header">Document Ingestion</div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1: b_file = st.file_uploader("Bank Statement", type=["csv","xlsx","xls","pdf"], key="itr_bank")
    with fc2: a_file = st.file_uploader("AIS / 26AS Document", type=["csv","xlsx","pdf"], key="itr_ais")
    with fc3: l_file = st.file_uploader("Stock P&L Ledger", type=["csv","xlsx","pdf"], key="itr_ledger")

    st.markdown("")
    if st.button("🚀  Execute Dual-Route Financial Synthesis", use_container_width=True):
        if not name or not pan:
            st.warning("⚠️ Enter Client Name and PAN to proceed.")
            return

        with st.spinner("Running compliance matrix..."):
            time.sleep(0.5)  # UX breathing room
            engine = RobustTaxEngine(bank_file=b_file, ledger_file=l_file)
            engine.salary_income            = salary
            engine.other_sources_income     = other_inc
            engine.total_deductions         = deductions
            engine.is_director_or_unlisted  = d_flag
            engine.has_foreign_assets       = f_flag
            engine.has_agri_over_5k         = a_flag
            engine.parse_bank_statement()
            engine.parse_stock_ledger()

            regime_key = "NEW" if "NEW" in regime else "OLD"
            result = engine.compute(route, regime_key)
            st.session_state.last_itr_result = result

            pdf_bytes = generate_itr_pdf(name, pan, user["firm"], result)
            st.session_state.itr_pdf_bytes    = pdf_bytes
            st.session_state.itr_pdf_filename = f"KSP_ITR_{pan}_AY2627.pdf"

        st.success(f"✅ Compliance framework generated for **{name}** | Profile: {profile_model}")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("ITR Form",            result["assigned_form"])
        m2.metric("Gross Receipts",      f"₹{result['metrics']['Gross Receipts / Turnover']:,.0f}")
        m3.metric("Net Taxable Income",  f"₹{result['metrics']['Net Taxable Income']:,.0f}")
        m4.metric("NET TAX PAYABLE",     f"₹{result['tax_breakdown']['NET TAX PAYABLE']:,.0f}")
        m5.metric("Sec 44AB Audit",      result["compliance_flags"]["Sec 44AB Audit Required"])

        st.markdown("---")
        t1, t2, t3 = st.tabs(["📊 Income Metrics", "⚖️ Tax Breakdown", "🚩 Compliance Flags"])
        with t1: st.json(result["metrics"])
        with t2: st.json(result["tax_breakdown"])
        with t3: st.json(result["compliance_flags"])

    if st.session_state.itr_pdf_bytes:
        st.markdown("---")
        st.download_button(
            "📥  Download Certified Compliance Report (PDF)",
            data=st.session_state.itr_pdf_bytes,
            file_name=st.session_state.itr_pdf_filename,
            mime="application/pdf",
            use_container_width=True
        )

# ─────────────────────────────────────────────
#  MODULE: GST COMMAND CENTER
# ─────────────────────────────────────────────
def render_gst_module(user):
    st.markdown('<div class="section-header">GST Entity Profile</div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        biz_name  = st.text_input("Business / Trade Name", placeholder="e.g. KSP Enterprises")
        gstin     = st.text_input("GSTIN (if registered)", placeholder="29ABCDE1234F1Z5", max_chars=15)
    with g2:
        state     = st.selectbox("State of Registration", ["Telangana","Karnataka","Maharashtra","Tamil Nadu","Delhi","Gujarat","Other"])
        biz_type  = st.selectbox("Business Category", ["Regular Taxpayer","Composition Dealer","E-Commerce Operator","Export / SEZ","Input Service Distributor"])
    with g3:
        itc_avail = st.number_input("ITC Available (₹)", min_value=0.0, step=100.0, format="%.2f")
        cash_paid = st.number_input("Tax Already Paid via Cash Ledger (₹)", min_value=0.0, step=100.0, format="%.2f")

    st.markdown('<div class="section-header">Supply Breakup by GST Rate</div>', unsafe_allow_html=True)
    sr1, sr2, sr3, sr4, sr5, sr6, sr7 = st.columns(7)
    supply_0   = sr1.number_input("0% (Exempt)", min_value=0.0, step=1000.0, format="%.2f")
    supply_5   = sr2.number_input("5%", min_value=0.0, step=1000.0, format="%.2f")
    supply_12  = sr3.number_input("12%", min_value=0.0, step=1000.0, format="%.2f")
    supply_18  = sr4.number_input("18%", min_value=0.0, step=1000.0, format="%.2f")
    supply_28  = sr5.number_input("28%", min_value=0.0, step=1000.0, format="%.2f")
    export_sup = sr6.number_input("Export (0%)", min_value=0.0, step=1000.0, format="%.2f")
    exempt_sup = sr7.number_input("Pure Exempt", min_value=0.0, step=1000.0, format="%.2f")

    if st.button("📊  Compute GST Liability & Filing Calendar", use_container_width=True):
        if not biz_name:
            st.warning("⚠️ Enter business name.")
            return

        with st.spinner("Processing GST matrix..."):
            time.sleep(0.3)
            gst = GSTEngine()
            gst.itc_claimed    = itc_avail
            gst.tax_paid_cash  = cash_paid
            gst.export_supply  = export_sup
            gst.exempt_supply  = exempt_sup
            gst.state          = state

            rate_struct = {"0%": supply_0, "5%": supply_5, "12%": supply_12, "18%": supply_18, "28%": supply_28}
            result = gst.compute_gst_liability(rate_struct)
            st.session_state.last_gst_result = result

            pdf_bytes = generate_gst_pdf(biz_name, gstin or "UNREGISTERED", user["firm"], result)
            st.session_state.gst_pdf_bytes = pdf_bytes

        st.success(f"✅ GST computation complete for **{biz_name}**")

        gm1, gm2, gm3, gm4 = st.columns(4)
        gm1.metric("Annual Turnover",     f"₹{result['annual_turnover']:,.0f}")
        gm2.metric("Gross Output Tax",    f"₹{result['summary']['Gross Output Tax']:,.0f}")
        gm3.metric("Net GST Payable",     f"₹{result['summary']['Net GST Payable']:,.0f}")
        gm4.metric("Cash Liability",      f"₹{result['summary']['Cash Ledger Requirement']:,.0f}")

        st.markdown("---")
        gt1, gt2, gt3 = st.tabs(["📋 Rate-wise Breakdown","📊 Summary","📅 Filing Calendar"])
        with gt1: st.json(result["rate_breakdown"])
        with gt2: st.json(result["summary"])
        with gt3: st.json(result["gstr_calendar"])

    if st.session_state.get("gst_pdf_bytes"):
        st.markdown("---")
        st.download_button(
            "📥  Download GST Compliance Report (PDF)",
            data=st.session_state.gst_pdf_bytes,
            file_name=f"KSP_GST_{(gstin or 'UNREG')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ─────────────────────────────────────────────
#  MODULE: AI COMPLIANCE AGENT (KSP AI)
# ─────────────────────────────────────────────
def render_ai_agent_module(user):
    st.markdown("""
    <div class="info-box">
    ⚡ <b>KSP AI Compliance & Filing Agent</b> — Powered by Claude API.
    Ask natural language questions about ITR, GST, TDS, AIS, or upload documents for AI-driven analysis.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Active Client Context</div>', unsafe_allow_html=True)
    ac1, ac2 = st.columns(2)
    with ac1:
        client_name    = st.text_input("Client Name (context)", placeholder="Dixith Chakravarthula")
        profile_model  = st.selectbox("Profile Model", [
            "Traditional Professional / Priest (Dakshina & Pooja Inflows)",
            "Salaried Professional", "Freelancer / Consultant",
            "Small Retailer", "Investor", "NRI"
        ])
    with ac2:
        connected_pipe = st.text_input("Connected Financial Pipeline Note", placeholder="e.g. Ledger text loaded from bank PDF")
        regime_sel     = st.selectbox("Preferred Regime for Analysis", ["NEW Regime (Sec 115BAC)", "OLD Regime"])

    st.markdown('<div class="section-header">Master Calculation Prompts / Directives</div>', unsafe_allow_html=True)
    user_prompt = st.text_area(
        "Enter your compliance query or directive:",
        height=120,
        placeholder="e.g. Perform parallel computing for both Standard Compliance and Credit Optimization layouts for Mr. Dixith Chakravarthula. Determine the exact recommended option based on audit protection rules."
    )

    if st.button("⚡  Execute Dual-Route Financial Synthesis", use_container_width=True):
        if not user_prompt.strip():
            st.warning("⚠️ Enter a directive to proceed.")
            return

        system_prompt = f"""You are KSP AI, an expert Indian tax and compliance assistant for AY 2026-27 (FY 2025-26).
You work for Kulkarni Strategic Partners, a professional B2B tax consultancy.
Current client: {client_name or 'Unknown'} | Profile: {profile_model} | Regime preference: {regime_sel}
Connected pipeline note: {connected_pipe or 'None'}

You must provide precise, actionable compliance guidance. Always reference:
- Correct ITR form selection logic (ITR-1 through ITR-6)
- AY 2026-27 tax slabs (New Regime: ₹0-4L: 0%, 4-8L: 5%, 8-12L: 10%, 12-16L: 15%, 16-20L: 20%, >20L: 30%)
- Post Finance Act 2024 capital gains rates (STCG 111A: 20%, LTCG 112A: 12.5%, exemption ₹1.25L)
- Section 87A rebate: ₹25,000 if income ≤ ₹12L (New Regime)
- GST thresholds and GSTR filing deadlines
- TDS provisions, Form 26AS cross-verification
- Sec 44AD / 44ADA presumptive scheme limits and conditions
Respond in a structured, professional format with clear sections and action items."""

        # Call Claude API
        import urllib.request
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1500,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        with st.spinner("KSP AI processing directive..."):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                    ai_response = "".join(b.get("text","") for b in data.get("content",[]))

                st.markdown("""
                <div class="ksp-card ksp-card-success">
                <div class="section-header" style="margin-top:0">AI Compliance Response</div>
                """, unsafe_allow_html=True)
                st.markdown(ai_response)
                st.markdown("</div>", unsafe_allow_html=True)

                # Show pipeline status
                if client_name:
                    st.markdown(f"""
                    <div class="ksp-card ksp-card-accent" style="margin-top:0.5rem; font-size:0.82rem;">
                    🔗 <b>Connected Financial Master Pipeline Active</b>: {connected_pipe or 'Manual input mode'}<br/>
                    • Active Client: <b>{client_name}</b> &nbsp;|&nbsp; • Profile Model: <b>{profile_model}</b>
                    </div>
                    """, unsafe_allow_html=True)

            except urllib.error.HTTPError as e:
                err_body = e.read().decode()
                st.error(f"Strategy Parallel Processing Error: {e.code} {e.reason}. {err_body}")
            except Exception as e:
                st.error(f"Strategy Parallel Processing Error: {str(e)}")

# ─────────────────────────────────────────────
#  MODULE: BUSINESS INCORPORATION MATRIX
# ─────────────────────────────────────────────
def render_incorporation_module(user):
    st.markdown("""
    <div class="info-box">
    📋 <b>Business Incorporation Strategy Matrix</b> — Compares entity structures (Pvt Ltd, LLP, OPC, Sole Prop, Partnership) 
    across tax, compliance, liability, and cost vectors for AY 2026-27.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Entity Profiling Parameters</div>', unsafe_allow_html=True)
    i1, i2, i3 = st.columns(3)
    with i1:
        promoter_count = st.number_input("Number of Promoters/Partners", min_value=1, max_value=200, value=2)
        annual_revenue = st.number_input("Projected Annual Revenue (₹)", min_value=0.0, step=100000.0, format="%.0f")
    with i2:
        foreign_inv    = st.checkbox("Requires Foreign Investment (FDI)")
        listed_plans   = st.checkbox("Plans to list on Stock Exchange (IPO)")
        vc_funding      = st.checkbox("Seeking VC / Angel Funding")
    with i3:
        sector         = st.selectbox("Business Sector", ["IT / Software Services","Manufacturing","Trading","Professional Services","E-Commerce","Healthcare","Other"])
        state_reg      = st.selectbox("State of Incorporation", ["Telangana","Karnataka","Maharashtra","Delhi","Tamil Nadu","Other"])

    if st.button("📊  Generate Incorporation Strategy Matrix", use_container_width=True):
        with st.spinner("Computing entity comparison matrix..."):
            time.sleep(0.3)

        entities = {
            "Private Limited Company": {
                "Tax Rate": "22% (Sec 115BAA) + Surcharge + 4% Cess",
                "Liability": "Limited to shareholding",
                "Compliance Load": "HIGH — ROC filings, board meetings, statutory audit mandatory",
                "FDI Eligible": "YES ✅",
                "Min Capital": "No minimum (post-2015)",
                "Recommended If": "VC funding, FDI, IPO track, >2 founders",
                "Estimated Annual Compliance Cost": "₹40,000 – ₹1,20,000",
            },
            "LLP (Limited Liability Partnership)": {
                "Tax Rate": "30% flat + 4% Cess (no MAT)",
                "Liability": "Limited",
                "Compliance Load": "MEDIUM — Annual return + statement of accounts",
                "FDI Eligible": "Limited (Automatic route restricted for some sectors)",
                "Min Capital": "No minimum",
                "Recommended If": "Professional firms, 2+ partners, moderate compliance tolerance",
                "Estimated Annual Compliance Cost": "₹15,000 – ₹40,000",
            },
            "One Person Company (OPC)": {
                "Tax Rate": "22% + Surcharge + 4% Cess",
                "Liability": "Limited",
                "Compliance Load": "MEDIUM",
                "FDI Eligible": "NO (single Indian resident only)",
                "Min Capital": "No minimum",
                "Recommended If": "Solo founder, wants corporate shield, revenue < ₹2Cr",
                "Estimated Annual Compliance Cost": "₹20,000 – ₹50,000",
            },
            "Sole Proprietorship": {
                "Tax Rate": "Individual slab rates (up to 30%)",
                "Liability": "UNLIMITED — Personal assets at risk",
                "Compliance Load": "LOW — ITR-3/4, GST if applicable",
                "FDI Eligible": "NO",
                "Min Capital": "None",
                "Recommended If": "Very small business, single person, minimal risk exposure",
                "Estimated Annual Compliance Cost": "₹5,000 – ₹15,000",
            },
            "Partnership Firm": {
                "Tax Rate": "30% flat + 4% Cess",
                "Liability": "UNLIMITED (unless LLP)",
                "Compliance Load": "LOW-MEDIUM",
                "FDI Eligible": "NO",
                "Min Capital": "None",
                "Recommended If": "Family business, traditional trade, avoid corporate formalities",
                "Estimated Annual Compliance Cost": "₹10,000 – ₹25,000",
            }
        }

        st.markdown('<div class="section-header">Entity Comparison Matrix</div>', unsafe_allow_html=True)
        for entity, details in entities.items():
            with st.expander(f"🏢 {entity}"):
                ec1, ec2 = st.columns(2)
                for i, (k, v) in enumerate(details.items()):
                    (ec1 if i % 2 == 0 else ec2).markdown(f"**{k}:** {v}")

        if foreign_inv or vc_funding or listed_plans:
            st.markdown("""
            <div class="ksp-card ksp-card-warning">
            ⭐ <b>Recommendation:</b> Given FDI/VC/IPO requirements, <b>Private Limited Company</b> is the only viable structure. 
            Register under Companies Act 2013 via MCA portal. Ensure MOA/AOA drafted with appropriate objects clause.
            </div>
            """, unsafe_allow_html=True)
        elif promoter_count == 1:
            st.markdown("""
            <div class="ksp-card ksp-card-accent">
            ⭐ <b>Recommendation:</b> Single promoter — consider <b>OPC</b> for corporate liability protection with lower compliance vs Pvt Ltd. 
            If revenue < ₹40L, Sole Proprietorship with ITR-4 (44AD) is simpler.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ksp-card ksp-card-success">
            ⭐ <b>Recommendation:</b> For professional services with multiple partners, <b>LLP</b> offers optimal balance of 
            liability protection, compliance cost, and pass-through flexibility.
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MODULE: PREDICTIVE CFO MODELING
# ─────────────────────────────────────────────
def render_cfo_module(user):
    st.markdown("""
    <div class="info-box">
    📈 <b>Predictive Fractional CFO Modeling</b> — Advance tax planning, cashflow projection, and 
    installment scheduling for AY 2026-27.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Income Projection Inputs</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        proj_revenue   = st.number_input("Projected Annual Revenue (₹)", min_value=0.0, step=50000.0, format="%.0f", value=2500000.0)
        proj_expenses  = st.number_input("Estimated Business Expenses (₹)", min_value=0.0, step=10000.0, format="%.0f", value=800000.0)
    with p2:
        proj_salary    = st.number_input("Salary / Fixed Income (₹)", min_value=0.0, step=10000.0, format="%.0f")
        proj_invest    = st.number_input("Expected Capital Gains (₹)", min_value=0.0, step=10000.0, format="%.0f")
    with p3:
        tds_deducted   = st.number_input("TDS Already Deducted (₹)", min_value=0.0, step=1000.0, format="%.0f")
        advance_paid   = st.number_input("Advance Tax Already Paid (₹)", min_value=0.0, step=1000.0, format="%.0f")

    if st.button("📈  Generate Advance Tax Schedule & CFO Forecast", use_container_width=True):
        with st.spinner("Computing advance tax schedule..."):
            time.sleep(0.3)

        # Simplified tax estimate
        net_income = max(0, proj_revenue - proj_expenses + proj_salary + proj_invest)
        # New regime slab (simplified)
        if net_income <= 400000:     est_tax = 0
        elif net_income <= 800000:   est_tax = (net_income - 400000) * 0.05
        elif net_income <= 1200000:  est_tax = 20000 + (net_income - 800000) * 0.10
        elif net_income <= 1600000:  est_tax = 60000 + (net_income - 1200000) * 0.15
        elif net_income <= 2000000:  est_tax = 120000 + (net_income - 1600000) * 0.20
        else:                        est_tax = 200000 + (net_income - 2000000) * 0.30
        est_tax_with_cess = est_tax * 1.04
        net_tax_after_tds = max(0, est_tax_with_cess - tds_deducted - advance_paid)

        # Advance tax installments (Sec 208/209)
        installments = {
            "1st Installment (by 15 Jun 2025)": max(0, est_tax_with_cess * 0.15),
            "2nd Installment (by 15 Sep 2025)": max(0, est_tax_with_cess * 0.45 - est_tax_with_cess * 0.15),
            "3rd Installment (by 15 Dec 2025)": max(0, est_tax_with_cess * 0.75 - est_tax_with_cess * 0.45),
            "4th Installment (by 15 Mar 2026)": max(0, est_tax_with_cess - est_tax_with_cess * 0.75),
        }

        am1, am2, am3, am4 = st.columns(4)
        am1.metric("Projected Net Income",    f"₹{net_income:,.0f}")
        am2.metric("Estimated Tax (with cess)", f"₹{est_tax_with_cess:,.0f}")
        am3.metric("TDS + Advance Paid",       f"₹{tds_deducted + advance_paid:,.0f}")
        am4.metric("Balance Tax Payable",      f"₹{net_tax_after_tds:,.0f}")

        st.markdown('<div class="section-header">Advance Tax Installment Schedule (Sec 208)</div>', unsafe_allow_html=True)
        for inst, amt in installments.items():
            col_a, col_b = st.columns([3,1])
            col_a.markdown(f"**{inst}**")
            col_b.markdown(f"₹ {amt:,.0f}")

        if net_tax_after_tds > 10_000:
            st.markdown(f"""
            <div class="ksp-card ksp-card-warning">
            ⚠️ <b>Advance Tax Alert:</b> Balance of ₹{net_tax_after_tds:,.0f} is payable. 
            Failure to pay advance tax attracts interest under Sec 234B (1% p.m.) and Sec 234C (1% p.m. per installment shortfall).
            Immediate action recommended.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ksp-card ksp-card-success">
            ✅ <b>Advance Tax:</b> TDS + advance payments appear adequate. Verify final figures with actual P&L at year-end.
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR — Module Navigator
# ─────────────────────────────────────────────
def render_sidebar(user):
    with st.sidebar:
        st.markdown("""
        <div style="padding:0.75rem 0; border-bottom:1px solid #30363D; margin-bottom:1rem;">
            <div style="font-family:'IBM Plex Mono';font-size:1rem;font-weight:700;color:#58A6FF;">⚙️ KSP CONSOLE</div>
            <div style="font-size:0.72rem;color:#8B949E;margin-top:2px;">PLATFORM</div>
        </div>
        """, unsafe_allow_html=True)

        modules = [
            ("itr",   "🚀 High-Value Smart ITR Filing Engine"),
            ("gst",   "🔵 GST Command Center Core"),
            ("ai",    "🌐 KSP AI Compliance & Filing Agent"),
            ("incorp","📋 Business Incorporation Strategy Matrix"),
            ("cfo",   "📈 Predictive Fractional CFO Modeling"),
        ]

        st.markdown('<div style="font-size:0.7rem;color:#8B949E;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem;">Choose functional module to execute:</div>', unsafe_allow_html=True)

        for key, label in modules:
            accessible = has_module_access(user["modules"], key)
            if accessible:
                if st.button(label, key=f"mod_{key}", use_container_width=True):
                    st.session_state.active_module = key
                    st.rerun()
            else:
                st.markdown(f'<div style="color:#484F58;font-size:0.82rem;padding:0.3rem 0;">🔒 {label}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:0.72rem;color:#8B949E;line-height:1.8;">
        <b style="color:#C9D1D9;">Firm:</b> {user['firm']}<br/>
        <b style="color:#C9D1D9;">Plan:</b> <span style="color:#3FB950;">{user['plan']}</span><br/>
        <b style="color:#C9D1D9;">User:</b> {user['username']}<br/>
        <b style="color:#C9D1D9;">AY:</b> 2026-27 (FY 2025-26)
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div style="font-size:0.7rem;color:#8B949E;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.4rem;">Architecture Framework: Unified Matrix Master v3.0</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.7rem;color:#3FB950;">🔒 Security Mode: Active</div>', unsafe_allow_html=True)
        st.markdown("")

        if st.button("⎋  Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ─────────────────────────────────────────────
#  MAIN APP CONTROLLER
# ─────────────────────────────────────────────
def render_main(user):
    render_sidebar(user)

    # Brand header bar
    module_titles = {
        "itr":   ("🚀", "High-Value Smart ITR Filing Engine", "AY 2026-27 | Sec 44AD/44ADA | New & Old Regime | Post Finance Act 2024"),
        "gst":   ("🔵", "GST Command Center Core", "Output Tax | ITC | GSTR Calendar | Registration Compliance"),
        "ai":    ("🌐", "KSP AI Compliance & Filing Agent", "Claude-powered natural language compliance assistant"),
        "incorp":("📋", "Business Incorporation Strategy Matrix", "Pvt Ltd | LLP | OPC | Partnership | Proprietorship"),
        "cfo":   ("📈", "Predictive Fractional CFO Modeling", "Advance Tax Schedule | Sec 208/234 | Cashflow Forecast"),
    }
    mod = st.session_state.active_module
    icon, title, subtitle = module_titles.get(mod, ("⚙️", "Module", ""))

    st.markdown(f"""
    <div class="brand-bar">
        <div class="logo">{icon}</div>
        <div>
            <div class="title">{title}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
        <div class="status-badge">● LIVE</div>
    </div>
    """, unsafe_allow_html=True)

    # Module router
    if mod == "itr":
        render_itr_module(user)
    elif mod == "gst":
        render_gst_module(user)
    elif mod == "ai":
        render_ai_agent_module(user)
    elif mod == "incorp":
        render_incorporation_module(user)
    elif mod == "cfo":
        render_cfo_module(user)

# ─────────────────────────────────────────────
#  ENTRYPOINT
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    render_login()
else:
    render_main(st.session_state.user)
