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
# ─────────────────────────────────────────────
B2B_USERS = {
    "admin"          : ("KSP@2026#Admin",  "Kulkarni Strategic Partners", "ENTERPRISE", "all"),
    "ca_shashank"    : ("Shashank@KSP1",   "Shashank Kulkarni & Associates", "PRO", "all"),
    "firm_abc"       : ("FirmABC@2026",    "ABC Tax Consultants", "STANDARD", ["itr", "gst"]),
    "firm_xyz"       : ("XYZ@Filing1",     "XYZ Financial Services", "PRO", "all"),
    "demo_user"      : ("Demo@1234",       "Demo Firm (Trial)", "TRIAL", ["itr"]),
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
#  LOGIN PAGE (Fixed Workflow)
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
        pwd = st.text_input("Password", type="password", placeholder="Enter password", key="login_p")
        st.markdown("")

        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        clicked = st.button("🔐 Authenticate & Enter Platform", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if clicked:
            result = authenticate(uname, pwd)
            if result:
                st.session_state.logged_in = True
                st.session_state.user = result
                st.success("Authentication successful! Redirecting...")
                time.sleep(0.5)
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
        self.stcg_111a               = 0.0
        self.stcg_other              = 0.0
        self.ltcg_112a               = 0.0
        self.ltcg_other              = 0.0
        self.salary_income           = 0.0
        self.other_sources_income    = 0.0
        self.total_deductions        = 0.0

        self.is_director_or_unlisted = False
        self.has_foreign_assets      = False
        self.has_agri_over_5k        = False

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
        full_text = ""
        page_texts = []
        for page in pdf.pages:
            t = page.extract_text() or ""
            page_texts.append(t)
            full_text += t + "\n"

        lines = full_text.split("\n")
        for i, line in enumerate(lines):
            if "BROUGHT FORWARD" in line.upper() or ("CR COUNT" in line.upper() and "DR COUNT" in line.upper()):
                search_block = "\n".join(lines[i:i+4])
                raw_nums = re.findall(r'([\d,]+\.\d{2})(?:CR|DR)?', search_block, re.IGNORECASE)
                clean_nums = []
                for n in raw_nums:
                    try:
                        clean_nums.append(float(n.replace(",", "")))
                    except:
                        pass
                amounts = [v for v in clean_nums if v > 500]
                if len(amounts) >= 2:
                    total_credits = amounts[-2]
                    if total_credits > 1000:
                        self.gross_receipts = round(total_credits, 2)
                        st.info(f"✅ Bank PDF parsed via Summary Row — Total Credits: ₹{total_credits:,.2f}")
                        return

        tc_patterns = [
            r'Total\s+Credits?\s*[\(₹\)]*\s*:?\s*([\d,]+\.\d{2})',
            r'Total\s+Cr(?:edits?)?\s+([\d,]+\.\d{2})',
            r'(?:Cr(?:edit)?\s+Amount|CREDIT\s+TOTAL)\s*:?\s*([\d,]+\.\d{2})',
        ]
        for pat in tc_patterns:
            m = re.search(pat, full_text, re.IGNORECASE)
            if m:
                try:
                    val = float(m.group(1).replace(",", ""))
                    if val > 1000:
                        self.gross_receipts = round(val, 2)
                        st.info(f"✅ Bank PDF parsed via Credit Label — Total Credits: ₹{val:,.2f}")
                        return
                except:
                    pass

        skip_keywords = ['WDL TFR', 'WDL', 'DEBIT', 'INTEREST CREDIT', 'CEMTEX', 'ATM', 'AMC', 'REVERSAL', 'ROLLBACK', 'FAILED']
        credit_keywords = ['DEP TFR', 'UPI/CR', 'NEFT CR', 'RTGS CR', 'IMPS CR', 'SALARY', 'TRANSFER CR', '/CR/', 'CR/']
        total = 0.0
        for page_text in page_texts:
            for line in page_text.split("\n"):
                u = line.upper()
                if not any(k in u for k in credit_keywords):
                    continue
                if any(k in u for k in skip_keywords):
                    continue
                nums = re.findall(r'\b(\d{1,3}(?:,\d{2,3})*\.\d{2})\b', line)
                clean = []
                for n in nums:
                    try:
                        v = float(n.replace(",", ""))
                        if v > 0:
                            clean.append(v)
                    except:
                        pass
                if len(clean) >= 2:
                    credit_candidate = clean[-2]
                    if credit_candidate > 0.5:
                        total += credit_candidate

        if total > 500:
            self.gross_receipts = round(total, 2)
            st.info(f"✅ Bank PDF parsed via Transaction Rows — Total Credits: ₹{total:,.2f}")
            return

        broad_total = 0.0
        for line in full_text.split("\n"):
            u = line.upper()
            if any(k in u for k in ['DEP', 'CR/', '/CR', 'CREDIT']):
                if any(k in u for k in ['WDL', 'DEBIT', 'INTEREST', 'CEMTEX']):
                    continue
                nums = re.findall(r'\b(\d{1,3}(?:,\d{2,3})*\.\d{2})\b', line)
                if len(nums) >= 2:
                    try:
                        broad_total += float(nums[-2].replace(",", ""))
                    except:
                        pass
        if broad_total > 0:
            self.gross_receipts = round(broad_total, 2)
            st.warning(f"⚠️ Bank PDF parsed via Broad Fallback — verify: ₹{broad_total:,.2f}")
        else:
            st.error("❌ Could not parse bank PDF. Please use CSV/XLSX export from your bank portal.")

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

    def compute(self, route, regime="NEW"):
        has_business = self.gross_receipts > 0
        has_cg = any([self.stcg_111a, self.stcg_other, self.ltcg_112a, self.ltcg_other])

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

        gross_total = (
            self.salary_income + self.presumptive_profit +
            self.stcg_111a + self.stcg_other +
            self.ltcg_112a + self.ltcg_other +
            self.other_sources_income
        )

        if regime == "NEW":
            net_taxable = max(0.0, gross_total)
            standard_deduction = min(75_000, self.salary_income) if self.salary_income > 0 else 0
            net_taxable = max(0.0, net_taxable - standard_deduction)
        else:
            net_taxable = max(0.0, gross_total - self.total_deductions)
            standard_deduction = min(50_000, self.salary_income) if self.salary_income > 0 else 0
            net_taxable = max(0.0, net_taxable - standard_deduction)

        special_cg = self.stcg_111a + self.stcg_other + self.ltcg_112a + self.ltcg_other
        slab_income = max(0.0, net_taxable - special_cg)

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
            if slab_income > 1_000_000:
                raw_slab_tax = (slab_income - 1_000_000)*0.30 + 112500
            elif slab_income > 500_000:
                raw_slab_tax = (slab_income - 500_000)*0.20 + 12500
            elif slab_income > 250_000:
                raw_slab_tax = (slab_income - 250_000)*0.05

        stcg_111a_tax  = self.stcg_111a * 0.20
        stcg_other_tax = 0.0

        ltcg_112a_exempt = 125_000
        ltcg_112a_tax = max(0.0, (self.ltcg_112a - ltcg_112a_exempt) * 0.125) if self.ltcg_112a > ltcg_112a_exempt else 0.0
        ltcg_other_tax = self.ltcg_other * 0.125

        total_pre_rebate = raw_slab_tax + stcg_111a_tax + stcg_other_tax + ltcg_112a_tax + ltcg_other_tax

        rebate_eligible_tax = raw_slab_tax
        if regime == "NEW":
            rebate = min(25_000, rebate_eligible_tax) if net_taxable <= 1_200_000 else 0.0
        else:
            rebate = min(12_500, rebate_eligible_tax) if net_taxable <= 500_000 else 0.0

        net_tax = max(0.0, total_pre_rebate - rebate)

        surcharge = 0.0
        if net_taxable > 5_000_000:
            surcharge_rate = 0.10 if net_taxable <= 10_000_000 else (0.15 if net_taxable <= 20_000_000 else 0.25)
            surcharge = net_tax * surcharge_rate

        cess = (net_tax + surcharge) * 0.04
        final_tax = round(net_tax + surcharge + cess, 2)

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
        gross_output_tax = 0.0
        breakdown = {}
        for rate_str, supply_val in rate_structure.items():
            rate = float(rate_str.replace("%","")) / 100
            tax = supply_val * rate
            igst = tax
            cgst = sgst = tax / 2
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

        reg_threshold  = 2_000_000
        comp_threshold = 15_000_000
        reg_required   = annual_turnover >= reg_threshold
        comp_eligible  = annual_turnover <= comp_threshold and self.exempt_supply == 0

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