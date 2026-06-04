"""
KSP CONSOLE PLATFORM — TaxSaaS B2B Engine v3.0
Kulkarni Strategic Partners | AY 2026-27
- Universal bank parser (SBI, HDFC, ICICI, Axis, Kotak, IDFC, YES, AU, Federal)
- ITR Engine linked to KSP AI — dual report (Standard + Credit Optimized) in one click
- All 5 modules fully functional
"""

import os, io, re, json, time, urllib.request
import pandas as pd
import numpy as np
import streamlit as st
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="KSP Console Platform", page_icon="⚙️",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;background-color:#0D1117;color:#E2E8F0;}
section[data-testid="stSidebar"]{background:#161B22!important;border-right:1px solid #30363D;}
section[data-testid="stSidebar"] *{color:#C9D1D9!important;}
.main .block-container{padding-top:1.5rem;}
.ksp-card{background:#161B22;border:1px solid #30363D;border-radius:8px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.ksp-card-accent{border-left:3px solid #58A6FF;}
.ksp-card-success{border-left:3px solid #3FB950;}
.ksp-card-warning{border-left:3px solid #D29922;}
.ksp-card-danger{border-left:3px solid #F85149;}
[data-testid="metric-container"]{background:#161B22;border:1px solid #30363D;border-radius:8px;padding:0.75rem 1rem;}
[data-testid="metric-container"] label{color:#8B949E!important;font-size:0.75rem!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#58A6FF!important;font-family:'IBM Plex Mono'!important;font-size:1.4rem!important;}
.stButton>button{background:#238636!important;color:#FFFFFF!important;border:1px solid #2EA043!important;border-radius:6px!important;font-family:'IBM Plex Sans'!important;font-weight:600!important;padding:0.5rem 1.25rem!important;transition:all 0.2s ease!important;}
.stButton>button:hover{background:#2EA043!important;box-shadow:0 0 10px rgba(46,160,67,0.4)!important;}
.login-btn>button{background:#1F6FEB!important;border:1px solid #388BFD!important;}
.login-btn>button:hover{background:#388BFD!important;}
.stTextInput>div>div>input,.stTextArea textarea{background:#0D1117!important;border:1px solid #30363D!important;border-radius:6px!important;color:#E2E8F0!important;font-family:'IBM Plex Mono'!important;}
.stTextInput>div>div>input:focus,.stTextArea textarea:focus{border-color:#58A6FF!important;}
.stSelectbox>div>div{background:#0D1117!important;border:1px solid #30363D!important;color:#E2E8F0!important;}
hr{border-color:#30363D!important;margin:1rem 0;}
.stTabs [data-baseweb="tab-list"]{background:#161B22!important;border-bottom:1px solid #30363D;gap:0;}
.stTabs [data-baseweb="tab"]{color:#8B949E!important;background:transparent!important;border-radius:0!important;font-size:0.85rem!important;padding:0.5rem 1rem!important;}
.stTabs [aria-selected="true"]{color:#58A6FF!important;border-bottom:2px solid #58A6FF!important;}
.brand-bar{display:flex;align-items:center;gap:12px;padding:0.6rem 0;border-bottom:1px solid #30363D;margin-bottom:1.5rem;}
.brand-bar .logo{font-size:1.5rem;}
.brand-bar .title{font-family:'IBM Plex Mono';font-size:1.1rem;font-weight:600;color:#58A6FF;letter-spacing:0.05em;}
.brand-bar .subtitle{font-size:0.75rem;color:#8B949E;margin-top:2px;}
.status-badge{margin-left:auto;background:#0D2818;border:1px solid #3FB950;color:#3FB950;border-radius:12px;padding:2px 10px;font-size:0.72rem;font-family:'IBM Plex Mono';}
.section-header{font-family:'IBM Plex Mono';font-size:0.7rem;font-weight:600;color:#8B949E;letter-spacing:0.12em;text-transform:uppercase;margin:1.25rem 0 0.6rem 0;border-bottom:1px solid #21262D;padding-bottom:4px;}
.info-box{background:#0C2A4A;border:1px solid #1F6FEB;border-radius:8px;padding:1rem 1.25rem;font-size:0.85rem;color:#58A6FF;margin-bottom:1rem;}
.login-container{max-width:420px;margin:6rem auto;background:#161B22;border:1px solid #30363D;border-radius:12px;padding:2.5rem;}
.login-logo{text-align:center;font-size:3rem;margin-bottom:0.5rem;}
.login-title{text-align:center;font-family:'IBM Plex Mono';font-size:1.2rem;color:#58A6FF;font-weight:600;}
.login-sub{text-align:center;font-size:0.8rem;color:#8B949E;margin-bottom:2rem;}
[data-testid="stDownloadButton"]>button{background:#161B22!important;border:1px solid #58A6FF!important;color:#58A6FF!important;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  B2B CREDENTIALS
# ─────────────────────────────────────────────
B2B_USERS = {
    "admin"      : ("KSP@2026#Admin",  "Kulkarni Strategic Partners",      "ENTERPRISE", "all"),
    "ca_shashank": ("Shashank@KSP1",   "Shashank Kulkarni & Associates",   "PRO",        "all"),
    "firm_abc"   : ("FirmABC@2026",    "ABC Tax Consultants",              "STANDARD",   ["itr","gst"]),
    "firm_xyz"   : ("XYZ@Filing1",     "XYZ Financial Services",           "PRO",        "all"),
    "demo_user"  : ("Demo@1234",       "Demo Firm (Trial)",                "TRIAL",      ["itr"]),
}

def authenticate(username, password):
    u = B2B_USERS.get(username.lower().strip())
    if u and u[0] == password:
        return {"username": username, "firm": u[1], "plan": u[2], "modules": u[3]}
    return None

def has_module_access(modules_allowed, key):
    return True if modules_allowed == "all" else key in modules_allowed

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "logged_in": False, "user": None, "active_module": "itr",
        "itr_pdf_bytes": None, "itr_pdf_filename": "",
        "opt_pdf_bytes": None, "opt_pdf_filename": "",
        "gst_pdf_bytes": None,
        "parsed_gross": 0.0, "parsed_stcg": 0.0, "parsed_ltcg": 0.0,
        "last_itr_result": None, "last_opt_result": None,
        "ai_itr_response": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
#  UNIVERSAL BANK PARSER
#  Handles: SBI, HDFC, ICICI, Axis, Kotak,
#  IDFC, YES Bank, AU, Federal, IndusInd,
#  PNB, BOB, Canara, Union, IOB
# ─────────────────────────────────────────────
class UniversalBankParser:
    @staticmethod
    def parse_pdf(file_obj) -> float:
        pdf = PdfReader(file_obj)
        page_texts = [p.extract_text() or "" for p in pdf.pages]
        full_text  = "\n".join(page_texts)

        # Pass 1: Check standard summary structural layouts
        val = UniversalBankParser._strategy_summary_row(full_text)
        if val > 0: return val

        # Pass 2: Check explicit label headers
        val = UniversalBankParser._strategy_summary_label(full_text)
        if val > 0: return val

        # Pass 3: Check isolated granular line items
        val = UniversalBankParser._strategy_transaction_rows(page_texts)
        if val > 0: return val

        # Pass 4: NEW AGGRESSIVE FALLBACK (Scans for multi-digit numbers appearing in right-hand columns)
        val = UniversalBankParser._strategy_deep_regex_extraction(full_text)
        return val or 0.0

    @staticmethod
    def _strategy_summary_row(full_text: str) -> float:
        trigger_phrases = [
            "BROUGHT FORWARD", "OPENING BALANCE", "CR COUNT", "TOTAL DEBIT",
            "STATEMENT SUMMARY", "ACCOUNT SUMMARY", "CLOSING BALANCE", "TOTAL CR"
        ]
        lines = full_text.split("\n")
        for i, line in enumerate(lines):
            u = line.upper()
            if any(ph in u for ph in trigger_phrases):
                block = "\n".join(lines[i:i+6])
                raw = re.findall(r'([\d,]+\.\d{2})(?:CR|DR)?', block, re.IGNORECASE)
                amounts = []
                for n in raw:
                    try:
                        v = float(n.replace(",",""))
                        if v > 1000: amounts.append(v)
                    except: pass
                if len(amounts) >= 1:
                    return round(max(amounts), 2)
        return 0.0

    @staticmethod
    def _strategy_summary_label(full_text: str) -> float:
        patterns = [
            r'Total\s+Cr(?:edit)?s?\s*[\(₹:)]*\s*([\d,]+\.\d{2})',
            r'(?:Sum|Total)\s+of\s+Credits?\s*:?\s*([\d,]+\.\d{2})',
            r'Credit\s+Turnover\s*:?\s*([\d,]+\.\d{2})',
            r'Total\s+Amount\s+Credited\s*:?\s*([\d,]+\.\d{2})',
            r'Aggregate\s+Credits?\s*:?\s*([\d,]+\.\d{2})',
            r'Total\s+Inward\s*:?\s*([\d,]+\.\d{2})',
        ]
        for pat in patterns:
            m = re.search(pat, full_text, re.IGNORECASE)
            if m:
                try:
                    v = float(m.group(1).replace(",",""))
                    if v > 0: return round(v, 2)
                except: pass
        return 0.0

    @staticmethod
    def _strategy_transaction_rows(page_texts: list) -> float:
        credit_tags  = ['DEP TFR','UPI/CR','NEFT CR','RTGS CR','IMPS CR','CR/','SALARY','CREDITED','TRANSFER CR','INWARD','BY ']
        skip_tags    = ['WDL TFR','WDL','UPI/DR','DEBIT','INTEREST CREDIT','ATM','AMC','FAILED']
        total = 0.0
        for text in page_texts:
            for line in text.split("\n"):
                u = line.upper()
                if not any(t in u for t in credit_tags): continue
                if any(t in u for t in skip_tags):       continue
                nums = re.findall(r'\b(\d{1,3}(?:,\d{2,3})*\.\d{2})\b', line)
                clean = []
                for n in nums:
                    try:
                        v = float(n.replace(",",""))
                        if v > 0: clean.append(v)
                    except: pass
                if len(clean) >= 1:
                    total += clean[-1]
        return round(total, 2) if total > 0 else 0.0

    @staticmethod
    def _strategy_deep_regex_extraction(full_text: str) -> float:
        """
        Aggressive token scanning for statements without clear structural tags.
        Finds large credit figures matching ledger spacing formats.
        """
        lines = full_text.split("\n")
        candidates = []
        for line in lines:
            if any(k in line.upper() for k in ["INTEREST", "BAL", "OPENING", "CLOSING"]): continue
            # Extract floating values with decimals
            nums = re.findall(r'\b(\d{2,3}(?:,\d{2,3})*\.\d{2})\b', line)
            for num in nums:
                try:
                    val = float(num.replace(",", ""))
                    if val > 5000.0:  # Filters micro-transactions or small balances
                        candidates.append(val)
                except: pass
        if candidates:
            # Safely returns the largest aggregate calculation signature or high match value
            return round(max(candidates), 2)
        return 0.0

    @staticmethod
    def parse_dataframe(df: pd.DataFrame) -> float:
        df.columns = [str(c).strip().upper() for c in df.columns]
        cr_col = next((c for c in df.columns if any(k in c for k in ['CREDIT','DEPOSIT','CR AMT','INWARD','AMOUNT CREDITED'])), None)
        if cr_col:
            df[cr_col] = pd.to_numeric(df[cr_col].astype(str).str.replace(",","").str.replace("CR",""), errors='coerce').fillna(0)
            return float(df[cr_col].sum())
        return 0.0

    @staticmethod
    def parse(file_obj) -> tuple:
        if not file_obj:
            return 0.0, "no_file"
        name = file_obj.name.lower()
        try:
            if name.endswith('.pdf'):
                val = UniversalBankParser.parse_pdf(file_obj)
                return val, "pdf_parser"
            elif name.endswith(('.xlsx','.xls')):
                df = pd.read_excel(file_obj, engine='openpyxl')
                val = UniversalBankParser.parse_dataframe(df)
                return val, "excel_parser"
            elif name.endswith('.csv'):
                for enc in ['utf-8','latin-1','cp1252']:
                    try:
                        file_obj.seek(0)
                        df = pd.read_csv(file_obj, encoding=enc)
                        val = UniversalBankParser.parse_dataframe(df)
                        return val, f"csv_parser({enc})"
                    except: continue
        except Exception as e:
            pass
        return 0.0, "failed"

# ─────────────────────────────────────────────
#  STOCK LEDGER PARSER
# ─────────────────────────────────────────────
class StockLedgerParser:
    @staticmethod
    def parse(file_obj) -> dict:
        result = {"stcg_111a":0.0,"ltcg_112a":0.0,"stcg_other":0.0,"ltcg_other":0.0}
        if not file_obj: return result
        name = file_obj.name.lower()
        try:
            if name.endswith(('.xlsx','.xls')):
                df = pd.read_excel(file_obj, engine='openpyxl')
                return StockLedgerParser._from_df(df)
            elif name.endswith('.csv'):
                df = pd.read_csv(file_obj)
                return StockLedgerParser._from_df(df)
            elif name.endswith('.pdf'):
                return StockLedgerParser._from_pdf(file_obj)
        except Exception as e:
            st.error(f"Ledger parsing error: {e}")
        return result

    @staticmethod
    def _from_pdf(file_obj) -> dict:
        r = {"stcg_111a":0.0,"ltcg_112a":0.0,"stcg_other":0.0,"ltcg_other":0.0}
        txt = "".join(p.extract_text() or "" for p in PdfReader(file_obj).pages)
        patterns = {
            "stcg_111a": r'(?:STCG|SHORT[\s\-]TERM\s*(?:EQUITY|LISTED|111A))[^\d]*?([\d,]+\.\d{2})',
            "ltcg_112a": r'(?:LTCG|LONG[\s\-]TERM\s*(?:EQUITY|LISTED|112A))[^\d]*?([\d,]+\.\d{2})',
            "stcg_other":r'(?:STCG[\s\-]*OTHER|SHORT[\s\-]TERM\s*DEBT)[^\d]*?([\d,]+\.\d{2})',
            "ltcg_other":r'(?:LTCG[\s\-]*OTHER|LONG[\s\-]TERM\s*DEBT)[^\d]*?([\d,]+\.\d{2})',
        }
        for k, pat in patterns.items():
            m = re.search(pat, txt, re.IGNORECASE)
            if m:
                try: r[k] = float(m.group(1).replace(",",""))
                except: pass
        return r

    @staticmethod
    def _from_df(df) -> dict:
        r = {"stcg_111a":0.0,"ltcg_112a":0.0,"stcg_other":0.0,"ltcg_other":0.0}
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapping = {
            "stcg_111a": ['STCG','SHORT TERM EQUITY','111A','SHORT-TERM','STCG 111A'],
            "ltcg_112a": ['LTCG','LONG TERM EQUITY','112A','LONG-TERM','LTCG 112A'],
            "stcg_other":['STCG OTHER','SHORT TERM DEBT','ST_OTHER','STCG-OTHER'],
            "ltcg_other":['LTCG OTHER','LONG TERM DEBT','LT_OTHER','LTCG-OTHER'],
        }
        for field, keys in mapping.items():
            col = next((c for c in df.columns if any(k in c for k in keys)), None)
            if col:
                r[field] = float(pd.to_numeric(
                    df[col].astype(str).str.replace(",",""), errors='coerce').sum())
        return r


# ─────────────────────────────────────────────
#  TAX ENGINE — AY 2026-27
# ─────────────────────────────────────────────
class TaxEngine:
    def __init__(self):
        self.gross_receipts       = 0.0
        self.presumptive_profit   = 0.0
        self.stcg_111a            = 0.0
        self.stcg_other           = 0.0
        self.ltcg_112a            = 0.0
        self.ltcg_other           = 0.0
        self.salary_income        = 0.0
        self.other_sources_income = 0.0
        self.total_deductions     = 0.0
        self.is_director          = False
        self.has_foreign_assets   = False
        self.has_agri_over_5k     = False

    def compute(self, route: str, regime: str = "NEW") -> dict:
        has_business = self.gross_receipts > 0
        has_cg = any([self.stcg_111a, self.stcg_other, self.ltcg_112a, self.ltcg_other])

        # ── ITR FORM SELECTION ────────────────
        if self.has_foreign_assets or self.is_director:
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

        # ── INCOME ────────────────────────────
        gross_total = (self.salary_income + self.presumptive_profit +
                       self.stcg_111a + self.stcg_other +
                       self.ltcg_112a + self.ltcg_other + self.other_sources_income)
        std_ded = min(75_000, self.salary_income) if regime == "NEW" and self.salary_income > 0 else (
                  min(50_000, self.salary_income) if regime == "OLD" and self.salary_income > 0 else 0)
        chapter_via = self.total_deductions if regime == "OLD" else 0.0
        net_taxable = max(0.0, gross_total - std_ded - chapter_via)

        # ── SLAB TAX ──────────────────────────
        special_cg = self.stcg_111a + self.ltcg_112a + self.ltcg_other
        slab_income = max(0.0, net_taxable - special_cg)
        raw_slab_tax = 0.0
        if regime == "NEW":
            # AY 2026-27 Budget 2025 slabs
            for (lo, hi, rate) in [(0,400000,0),(400000,800000,0.05),(800000,1200000,0.10),
                                    (1200000,1600000,0.15),(1600000,2000000,0.20),(2000000,float('inf'),0.30)]:
                if slab_income > lo:
                    raw_slab_tax += (min(slab_income, hi) - lo) * rate
        else:
            for (lo, hi, rate) in [(0,250000,0),(250000,500000,0.05),(500000,1000000,0.20),(1000000,float('inf'),0.30)]:
                if slab_income > lo:
                    raw_slab_tax += (min(slab_income, hi) - lo) * rate

        # ── CAPITAL GAINS TAX — Finance Act 2024 ──
        stcg_111a_tax = self.stcg_111a * 0.20          # 20% post Jul 2024
        ltcg_112a_tax = max(0.0, (self.ltcg_112a - 125_000) * 0.125) if self.ltcg_112a > 125_000 else 0.0
        ltcg_other_tax = self.ltcg_other * 0.125

        total_pre_rebate = raw_slab_tax + stcg_111a_tax + ltcg_112a_tax + ltcg_other_tax

        # ── SEC 87A REBATE ────────────────────
        if regime == "NEW":
            rebate = min(25_000, raw_slab_tax) if net_taxable <= 1_200_000 else 0.0
        else:
            rebate = min(12_500, raw_slab_tax) if net_taxable <= 500_000 else 0.0

        net_tax = max(0.0, total_pre_rebate - rebate)

        # ── SURCHARGE ─────────────────────────
        surcharge = 0.0
        if net_taxable > 5_000_000:
            r = 0.10 if net_taxable<=10_000_000 else (0.15 if net_taxable<=20_000_000 else 0.25)
            surcharge = net_tax * r

        cess = (net_tax + surcharge) * 0.04
        final_tax = round(net_tax + surcharge + cess, 2)

        audit_req = (has_business and self.gross_receipts > 10_000_000) or \
                    ("44AD"  in route and self.gross_receipts > 0 and self.presumptive_profit < self.gross_receipts * 0.06) or \
                    ("44ADA" in route and self.gross_receipts > 0 and self.presumptive_profit < self.gross_receipts * 0.50)

        return {
            "assigned_form": itr_form,
            "regime": regime,
            "audit_required": audit_req,
            "metrics": {
                "Gross Receipts / Turnover":               round(self.gross_receipts, 2),
                "Presumptive Profit (44AD/44ADA)":         round(self.presumptive_profit, 2),
                "Salary Income":                           round(self.salary_income, 2),
                "Standard Deduction":                      round(std_ded, 2),
                "STCG — Sec 111A (Listed Equity 20%)":    round(self.stcg_111a, 2),
                "STCG — Other (Slab Rate)":               round(self.stcg_other, 2),
                "LTCG — Sec 112A (Listed Equity 12.5%)":  round(self.ltcg_112a, 2),
                "LTCG — Other (12.5%)":                   round(self.ltcg_other, 2),
                "Other Source Income":                     round(self.other_sources_income, 2),
                "Chapter VIA Deductions (Old Regime)":    round(chapter_via, 2),
                "Gross Total Income (GTI)":               round(gross_total, 2),
                "Net Taxable Income":                     round(net_taxable, 2),
            },
            "tax_breakdown": {
                "Slab Tax":                   round(raw_slab_tax, 2),
                "STCG Tax 111A @ 20%":        round(stcg_111a_tax, 2),
                "LTCG Tax 112A @ 12.5%":      round(ltcg_112a_tax, 2),
                "LTCG Other @ 12.5%":         round(ltcg_other_tax, 2),
                "Total Pre-Rebate Tax":        round(total_pre_rebate, 2),
                "Section 87A Rebate":          round(rebate, 2),
                "Surcharge":                  round(surcharge, 2),
                "Health & Education Cess 4%": round(cess, 2),
                "NET TAX PAYABLE":            round(final_tax, 2),
            },
            "compliance_flags": {
                "Sec 44AB Audit Required":    "YES ⚠️" if audit_req else "NO ✅",
                "Foreign Assets (Schedule FA)": "YES — Required" if self.has_foreign_assets else "NOT APPLICABLE",
                "Directorship / Unlisted":    "YES — ITR-3 Mandatory" if self.is_director else "NOT APPLICABLE",
                "Agricultural Income":        "YES — Partial Integration" if self.has_agri_over_5k else "NOT APPLICABLE",
            }
        }


# ─────────────────────────────────────────────
#  GST ENGINE
# ─────────────────────────────────────────────
class GSTEngine:
    def compute(self, itc, cash_paid, export_sup, exempt_sup, rate_struct: dict) -> dict:
        gross_output_tax = 0.0
        breakdown = {}
        for rate_str, supply_val in rate_struct.items():
            rate = float(rate_str.replace("%","")) / 100
            tax  = supply_val * rate
            gross_output_tax += tax
            breakdown[rate_str] = {
                "Taxable Value": round(supply_val,2),
                "Output Tax": round(tax,2),
                "CGST": round(tax/2,2),
                "SGST/IGST": round(tax/2,2),
            }
        net_payable  = max(0.0, gross_output_tax - itc)
        cash_req     = max(0.0, net_payable - cash_paid)
        annual_to    = sum(rate_struct.values()) + exempt_sup + export_sup
        return {
            "annual_turnover": round(annual_to, 2),
            "registration_required": annual_to >= 2_000_000,
            "composition_eligible":  annual_to <= 15_000_000 and exempt_sup == 0,
            "rate_breakdown": breakdown,
            "summary": {
                "Gross Output Tax":       round(gross_output_tax,2),
                "ITC Available":          round(itc,2),
                "Net GST Payable":        round(net_payable,2),
                "Cash Ledger Requirement":round(cash_req,2),
                "Export (Zero-Rated)":    round(export_sup,2),
                "Exempt Supply":          round(exempt_sup,2),
            },
            "gstr_calendar": {
                "GSTR-1":  "11th of following month (or quarterly QRMP)",
                "GSTR-3B": "20th of following month",
                "GSTR-9":  "31st December (turnover > ₹2Cr)",
                "GSTR-9C": "31st December (turnover > ₹5Cr)",
            },
            "compliance_flags": {
                "GST Registration": "REQUIRED ✅" if annual_to >= 2_000_000 else "BELOW THRESHOLD",
                "Composition Eligible": "YES" if annual_to <= 15_000_000 else "NO",
                "LUT for Export": "YES — File LUT" if export_sup > 0 else "NOT APPLICABLE",
            }
        }


# ─────────────────────────────────────────────
#  GEMINI API HELPER
# ─────────────────────────────────────────────
def call_gemini(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY",""))
    if not GEMINI_API_KEY:
        return "❌ GEMINI_API_KEY not configured. Add it in Streamlit Secrets."
    combined = f"{system_prompt}\n\n---\n\nUser Query:\n{user_prompt}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": combined}], "role": "user"}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.3}
    }).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        return f"❌ Gemini API error {e.code}: {e.read().decode()}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

KSP_SYSTEM_PROMPT = """You are KSP AI, an expert Indian tax and compliance assistant for AY 2026-27 (FY 2025-26).
You work for Kulkarni Strategic Partners, a professional B2B tax consultancy.

Always use these exact AY 2026-27 rules:
- New Regime slabs (Budget 2025): 0-4L:0%, 4-8L:5%, 8-12L:10%, 12-16L:15%, 16-20L:20%, >20L:30%
- Old Regime slabs: 0-2.5L:0%, 2.5-5L:5%, 5-10L:20%, >10L:30%
- STCG Sec 111A (listed equity): 20% (Finance Act 2024 — was 15%)
- LTCG Sec 112A (listed equity): 12.5% with ₹1.25L exemption (Finance Act 2024 — was 10%/₹1L)
- Section 87A (New Regime): ₹25,000 rebate if net taxable ≤ ₹12L
- Section 87A (Old Regime): ₹12,500 rebate if net taxable ≤ ₹5L
- Standard Deduction: ₹75,000 (New), ₹50,000 (Old)
- Sec 44AD turnover limit: ₹3Cr (digital), presumptive: 6%
- Sec 44ADA limit: ₹75L, presumptive: 50%
- Sec 44AB audit: triggered if turnover > ₹1Cr (cash) / ₹10Cr (digital)

Respond with structured sections, concrete numbers, and actionable filing steps.
For dual-report requests, always produce BOTH: (A) Standard Compliance and (B) Credit Optimization layout."""


# ─────────────────────────────────────────────
#  PDF GENERATOR — ITR REPORT
# ─────────────────────────────────────────────
def generate_itr_pdf(name, pan, firm, result, report_type="Standard Compliance"):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=40, rightMargin=40,
                             topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=14,
                              textColor=colors.HexColor("#1A365D"), spaceAfter=6)
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=11,
                              textColor=colors.HexColor("#2C5282"), spaceBefore=10, spaceAfter=4)
    body_s  = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=13)
    bold_s  = ParagraphStyle('Bo', parent=body_s, fontName='Helvetica-Bold')
    small_s = ParagraphStyle('S', parent=styles['Normal'], fontSize=7,
                              textColor=colors.HexColor("#888"))
    story = []

    story.append(Paragraph(f"KSP CONSOLE PLATFORM — {report_type} Report", title_s))
    story.append(Paragraph(f"Kulkarni Strategic Partners · {firm}", body_s))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#CBD5E0"), spaceAfter=10))

    meta = [
        [Paragraph(f"<b>Assessee:</b> {name}", body_s),
         Paragraph(f"<b>AY:</b> 2026-27 (FY 2025-26)", body_s)],
        [Paragraph(f"<b>PAN:</b> {pan}", body_s),
         Paragraph(f"<b>ITR Form:</b> {result['assigned_form']}", body_s)],
        [Paragraph(f"<b>Regime:</b> {result['regime']} REGIME (Sec 115BAC)", body_s),
         Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%d %b %Y %H:%M')}", body_s)],
    ]
    t = Table(meta, colWidths=[265,265])
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
                            ('PADDING',(0,0),(-1,-1),5),
                            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#EDF2F7"))]))
    story.append(t); story.append(Spacer(1,12))

    story.append(Paragraph("I. Income Ingestion Summary", h2_s))
    rows = [[Paragraph("<b>Field</b>",body_s), Paragraph("<b>Amount (INR)</b>",body_s)]]
    for k,v in result["metrics"].items():
        rows.append([Paragraph(k,body_s), Paragraph(f"₹ {v:,.2f}",body_s)])
    t2 = Table(rows, colWidths=[370,160])
    t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#EDF2F7")),
                             ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
                             ('PADDING',(0,0),(-1,-1),4)]))
    story.append(t2); story.append(Spacer(1,12))

    story.append(Paragraph("II. Tax Computation Matrix", h2_s))
    rows2 = [[Paragraph("<b>Component</b>",body_s), Paragraph("<b>Amount (INR)</b>",body_s)]]
    for k,v in result["tax_breakdown"].items():
        s = bold_s if "NET TAX" in k else body_s
        rows2.append([Paragraph(f"<b>{k}</b>" if "NET TAX" in k else k, s),
                      Paragraph(f"₹ {v:,.2f}", s)])
    t3 = Table(rows2, colWidths=[370,160])
    t3.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#EDF2F7")),
                             ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
                             ('PADDING',(0,0),(-1,-1),4),
                             ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor("#E2E8F0"))]))
    story.append(t3); story.append(Spacer(1,12))

    story.append(Paragraph("III. Compliance Flags", h2_s))
    for k,v in result["compliance_flags"].items():
        story.append(Paragraph(f"<b>{k}:</b> {v}", body_s))
        story.append(Spacer(1,3))
    story.append(Spacer(1,10))

    story.append(Paragraph("IV. Step-by-Step E-Filing Blueprint", h2_s))
    net_tax = result['tax_breakdown']['NET TAX PAYABLE']
    rebate  = result['tax_breakdown']['Section 87A Rebate']
    steps = [
        f"<b>Step 1 — Form:</b> incometax.gov.in → File ITR → AY 2026-27 → <b>{result['assigned_form']}</b>.",
        f"<b>Step 2 — Regime:</b> Select <b>{result['regime']} REGIME</b> (Sec 115BAC). Confirm before proceeding.",
        f"<b>Step 3 — Schedule BP:</b> Gross Receipts: <b>₹{result['metrics']['Gross Receipts / Turnover']:,.2f}</b> | Presumptive Profit: <b>₹{result['metrics']['Presumptive Profit (44AD/44ADA)']:,.2f}</b>",
        f"<b>Step 4 — Schedule CG:</b> Sec 111A STCG: <b>₹{result['metrics']['STCG — Sec 111A (Listed Equity 20%)']:,.2f}</b> @ 20% | Sec 112A LTCG: <b>₹{result['metrics']['LTCG — Sec 112A (Listed Equity 12.5%)']:,.2f}</b> @ 12.5%",
        f"<b>Step 5 — Part B-TTI:</b> Sec 87A Rebate: <b>₹{rebate:,.2f}</b> | NET TAX: <b>₹{net_tax:,.2f}</b>",
        "<b>Step 6 — Pre-Submit:</b> Cross-verify all TDS credits with Form 26AS and AIS.",
        "<b>Step 7 — E-Verify:</b> Submit → Preview → E-Verify via Aadhaar OTP within 30 days.",
    ]
    for s in steps:
        story.append(Paragraph(s, body_s)); story.append(Spacer(1,4))

    story.append(Spacer(1,15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0")))
    story.append(Paragraph(
        "Disclaimer: This report is generated by KSP Console Platform for professional reference only. "
        "Verify all figures with source documents before filing.", small_s))
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def generate_gst_pdf(biz_name, gstin, firm, result):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=40, rightMargin=40,
                             topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=14,
                              textColor=colors.HexColor("#1A365D"), spaceAfter=6)
    h2_s   = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=11,
                              textColor=colors.HexColor("#2C5282"), spaceBefore=10, spaceAfter=4)
    body_s = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=13)
    story  = []
    story.append(Paragraph("KSP CONSOLE PLATFORM — GST Compliance Report", title_s))
    story.append(Paragraph(f"Kulkarni Strategic Partners · {firm}", body_s))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#CBD5E0"), spaceAfter=10))
    meta = [
        [Paragraph(f"<b>Business:</b> {biz_name}", body_s),
         Paragraph(f"<b>GSTIN:</b> {gstin}", body_s)],
        [Paragraph(f"<b>Turnover:</b> ₹{result['annual_turnover']:,.2f}", body_s),
         Paragraph(f"<b>Registration:</b> {result['compliance_flags']['GST Registration']}", body_s)],
    ]
    t = Table(meta, colWidths=[265,265])
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
                            ('PADDING',(0,0),(-1,-1),5),
                            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#EDF2F7"))]))
    story.append(t); story.append(Spacer(1,12))
    story.append(Paragraph("I. GST Summary", h2_s))
    rows = [[Paragraph("<b>Component</b>",body_s), Paragraph("<b>Amount (INR)</b>",body_s)]]
    for k,v in result["summary"].items():
        rows.append([Paragraph(k,body_s), Paragraph(f"₹ {v:,.2f}",body_s)])
    t2 = Table(rows, colWidths=[370,160])
    t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#EDF2F7")),
                             ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
                             ('PADDING',(0,0),(-1,-1),4)]))
    story.append(t2); story.append(Spacer(1,10))
    story.append(Paragraph("II. GSTR Filing Calendar", h2_s))
    for form, due in result["gstr_calendar"].items():
        story.append(Paragraph(f"<b>{form}:</b> {due}", body_s))
        story.append(Spacer(1,3))
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


# ─────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────
def render_login():
    st.markdown("""
    <div class="login-container">
        <div class="login-logo">⚙️</div>
        <div class="login-title">KSP CONSOLE PLATFORM</div>
        <div class="login-sub">B2B Tax & Compliance SaaS · AY 2026-27<br/>Authorised Firm Access Only</div>
    </div>""", unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    with col:
        uname = st.text_input("Username", placeholder="Enter your firm username", key="login_u")
        pwd   = st.text_input("Password", type="password", placeholder="Enter password", key="login_p")
        st.markdown("")
        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("🔐  Authenticate & Enter Platform", use_container_width=True):
            result = authenticate(uname, pwd)
            if result:
                st.session_state.logged_in = True
                st.session_state.user = result
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Contact your KSP administrator.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""<div style="text-align:center;margin-top:1.5rem;font-size:0.75rem;color:#484F58;">
        🔒 Encrypted session · Authorised clients only<br/>Contact: admin@kspfiling.in for access
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MODULE: HIGH-VALUE SMART ITR ENGINE
#  (Linked to KSP AI — dual report on one click)
# ─────────────────────────────────────────────
def render_itr_module(user):
    # ── CLIENT PROFILE ────────────────────────
    st.markdown('<div class="section-header">Active Client Configuration</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Client Legal Name", placeholder="e.g. Dixith Chakravarthula")
        pan  = st.text_input("PAN Number", placeholder="ABCDE1234F", max_chars=10)
    with c2:
        salary    = st.number_input("Salary Income (₹)", min_value=0.0, step=1000.0, format="%.2f")
        other_inc = st.number_input("Other Sources Income (₹)", min_value=0.0, step=1000.0, format="%.2f")
    with c3:
        deductions = st.number_input("Chapter VIA Deductions (₹) [Old Regime only]",
                                      min_value=0.0, step=1000.0, format="%.2f")
        regime     = st.selectbox("Tax Regime", ["NEW (Sec 115BAC)", "OLD (Regular)"])

    st.markdown('<div class="section-header">Business Route & Compliance Flags</div>', unsafe_allow_html=True)
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
        profile_model = st.selectbox("Client Profile", [
            "Salaried Professional",
            "Traditional Professional / Priest (Dakshina & Pooja Inflows)",
            "Freelancer / Consultant",
            "Small Retailer / Trader",
            "Investor (Equity & MF)",
            "HUF",
            "NRI / Foreign Income",
        ])

    # ── DOCUMENT INGESTION ─────────────────────
    st.markdown('<div class="section-header">Document Ingestion</div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1: b_file = st.file_uploader("Bank Statement (any bank — PDF/CSV/XLSX)",
                                         type=["csv","xlsx","xls","pdf"], key="itr_bank")
    with fc2: a_file = st.file_uploader("AIS / 26AS (optional)",
                                         type=["csv","xlsx","pdf"], key="itr_ais")
    with fc3: l_file = st.file_uploader("Stock P&L Ledger (optional)",
                                         type=["csv","xlsx","pdf"], key="itr_ledger")

    # ── STEP 1: PARSE ─────────────────────────
    st.markdown('<div class="section-header">Step 1 — Parse Documents & Verify Figures</div>',
                unsafe_allow_html=True)

    if st.button("🔍  Parse Uploaded Documents", use_container_width=False):
        with st.spinner("Parsing bank statement & ledger..."):
            gross, strategy = UniversalBankParser.parse(b_file)
            ledger_data     = StockLedgerParser.parse(l_file)
            st.session_state.parsed_gross = gross
            st.session_state.parsed_stcg  = ledger_data["stcg_111a"]
            st.session_state.parsed_ltcg  = ledger_data["ltcg_112a"]
            if gross > 0:
                st.success(f"✅ Bank parsed via **{strategy}** — Total Credits: ₹{gross:,.2f}")
            else:
                st.warning("⚠️ Could not auto-parse bank. Enter Gross Receipts manually below.")

    ov1, ov2, ov3 = st.columns(3)
    with ov1:
        gross_receipts = st.number_input(
            "✏️ Gross Receipts / Total Bank Credits (₹)",
            value=float(st.session_state.get("parsed_gross", 0.0)),
            min_value=0.0, step=100.0, format="%.2f", key="itr_gross",
            help="Auto-filled from bank parse. Edit if incorrect.")
    with ov2:
        stcg_val = st.number_input(
            "✏️ STCG — Sec 111A Listed Equity (₹)",
            value=float(st.session_state.get("parsed_stcg", 0.0)),
            min_value=0.0, step=100.0, format="%.2f", key="itr_stcg")
    with ov3:
        ltcg_val = st.number_input(
            "✏️ LTCG — Sec 112A Listed Equity (₹)",
            value=float(st.session_state.get("parsed_ltcg", 0.0)),
            min_value=0.0, step=100.0, format="%.2f", key="itr_ltcg")

    # ── STEP 2: COMPUTE + AI DUAL REPORT ──────
    st.markdown('<div class="section-header">Step 2 — Compute Tax + AI Dual Report (Standard & Credit Optimized)</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="margin-bottom:0.75rem;">
    ⚡ <b>One-Click Dual Report</b> — Clicking Execute below will:<br/>
    &nbsp;&nbsp;① Compute both New Regime and Old Regime tax<br/>
    &nbsp;&nbsp;② Send data to KSP AI for Credit Optimization analysis<br/>
    &nbsp;&nbsp;③ Generate two PDF reports — Standard Compliance + AI-Optimized
    </div>""", unsafe_allow_html=True)

    if st.button("🚀  Execute: Compute + AI Dual-Route Analysis + Generate Reports",
                  use_container_width=True):
        if not name or not pan:
            st.warning("⚠️ Enter Client Name and PAN to proceed.")
            return
        if len(pan) != 10:
            st.warning("⚠️ PAN must be 10 characters.")
            return

        regime_key = "NEW" if "NEW" in regime else "OLD"

        with st.spinner("Running tax computation matrix..."):
            # ── Standard computation ──
            eng = TaxEngine()
            eng.gross_receipts       = gross_receipts
            eng.stcg_111a            = stcg_val
            eng.ltcg_112a            = ltcg_val
            eng.salary_income        = salary
            eng.other_sources_income = other_inc
            eng.total_deductions     = deductions
            eng.is_director          = d_flag
            eng.has_foreign_assets   = f_flag
            eng.has_agri_over_5k     = a_flag
            result_std = eng.compute(route, regime_key)

            # ── Alternate regime computation ──
            alt_regime = "OLD" if regime_key == "NEW" else "NEW"
            eng2 = TaxEngine()
            eng2.gross_receipts       = gross_receipts
            eng2.stcg_111a            = stcg_val
            eng2.ltcg_112a            = ltcg_val
            eng2.salary_income        = salary
            eng2.other_sources_income = other_inc
            eng2.total_deductions     = deductions
            eng2.is_director          = d_flag
            eng2.has_foreign_assets   = f_flag
            eng2.has_agri_over_5k     = a_flag
            result_alt = eng2.compute(route, alt_regime)

            st.session_state.last_itr_result = result_std

        with st.spinner("KSP AI generating credit optimization analysis..."):
            ai_prompt = f"""Generate a complete dual-route compliance report for:
Client: {name} | PAN: {pan} | Profile: {profile_model}
Gross Receipts: ₹{gross_receipts:,.2f}
Salary: ₹{salary:,.2f} | Other Income: ₹{other_inc:,.2f}
STCG (111A): ₹{stcg_val:,.2f} | LTCG (112A): ₹{ltcg_val:,.2f}
Chapter VIA Deductions: ₹{deductions:,.2f}
Filing Route: {route}
Preferred Regime: {regime_key} | Alternate: {alt_regime}

COMPUTED RESULTS:
{regime_key} Regime — ITR Form: {result_std['assigned_form']} | Net Taxable: ₹{result_std['metrics']['Net Taxable Income']:,.2f} | NET TAX: ₹{result_std['tax_breakdown']['NET TAX PAYABLE']:,.2f}
{alt_regime} Regime — ITR Form: {result_alt['assigned_form']} | Net Taxable: ₹{result_alt['metrics']['Net Taxable Income']:,.2f} | NET TAX: ₹{result_alt['tax_breakdown']['NET TAX PAYABLE']:,.2f}

Produce:
A) STANDARD COMPLIANCE REPORT — confirm all figures, flag any issues, provide e-filing steps.
B) CREDIT OPTIMIZATION REPORT — identify tax-saving opportunities, recommend optimal regime, suggest deductions/investments (80C/80D/NPS/HRA), calculate maximum tax savings possible, and give final recommended action with exact savings amount.
Be specific with rupee amounts. Format clearly with headers."""

            ai_response = call_gemini(KSP_SYSTEM_PROMPT, ai_prompt, max_tokens=2500)
            st.session_state.ai_itr_response = ai_response

        with st.spinner("Generating PDF reports..."):
            pdf_std = generate_itr_pdf(name, pan, user["firm"], result_std, "Standard Compliance")
            pdf_opt = generate_itr_pdf(name, pan, user["firm"], result_alt, f"Credit Optimized — {alt_regime} Regime")
            st.session_state.itr_pdf_bytes    = pdf_std
            st.session_state.itr_pdf_filename = f"KSP_ITR_Standard_{pan}_AY2627.pdf"
            st.session_state.opt_pdf_bytes    = pdf_opt
            st.session_state.opt_pdf_filename = f"KSP_ITR_Optimized_{pan}_AY2627.pdf"

        st.success(f"✅ Dual-route analysis complete for **{name}**")

        # ── METRICS DASHBOARD ──
        st.markdown('<div class="section-header">Tax Comparison — Both Regimes</div>',
                    unsafe_allow_html=True)
        mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
        mc1.metric("ITR Form",          result_std["assigned_form"])
        mc2.metric(f"{regime_key} Regime Tax",
                   f"₹{result_std['tax_breakdown']['NET TAX PAYABLE']:,.0f}")
        mc3.metric(f"{alt_regime} Regime Tax",
                   f"₹{result_alt['tax_breakdown']['NET TAX PAYABLE']:,.0f}")
        saving = abs(result_std['tax_breakdown']['NET TAX PAYABLE'] -
                     result_alt['tax_breakdown']['NET TAX PAYABLE'])
        better = regime_key if result_std['tax_breakdown']['NET TAX PAYABLE'] <= \
                                result_alt['tax_breakdown']['NET TAX PAYABLE'] else alt_regime
        mc4.metric("Potential Saving",  f"₹{saving:,.0f}")
        mc5.metric("Recommended Regime", better)
        mc6.metric("Sec 44AB Audit",    result_std["compliance_flags"]["Sec 44AB Audit Required"])

        st.markdown("---")

        # ── AI DUAL REPORT ──
        st.markdown('<div class="section-header">KSP AI — Standard & Credit Optimization Analysis</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="ksp-card ksp-card-success">
        {st.session_state.ai_itr_response}
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        t1, t2, t3, t4 = st.tabs([
            f"📊 {regime_key} Regime Metrics",
            f"📊 {alt_regime} Regime Metrics",
            "⚖️ Tax Breakdown",
            "🚩 Compliance Flags"
        ])
        with t1: st.json(result_std["metrics"])
        with t2: st.json(result_alt["metrics"])
        with t3:
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**{regime_key} Regime**"); col_a.json(result_std["tax_breakdown"])
            col_b.markdown(f"**{alt_regime} Regime**"); col_b.json(result_alt["tax_breakdown"])
        with t4: st.json(result_std["compliance_flags"])

    # ── DOWNLOAD BUTTONS ──
    if st.session_state.itr_pdf_bytes:
        st.markdown("---")
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button("📥  Download Standard Compliance PDF",
                data=st.session_state.itr_pdf_bytes,
                file_name=st.session_state.itr_pdf_filename,
                mime="application/pdf", use_container_width=True)
        with dl2:
            if st.session_state.opt_pdf_bytes:
                st.download_button("📥  Download Credit Optimized PDF",
                    data=st.session_state.opt_pdf_bytes,
                    file_name=st.session_state.opt_pdf_filename,
                    mime="application/pdf", use_container_width=True)


# ─────────────────────────────────────────────
#  MODULE: GST COMMAND CENTER
# ─────────────────────────────────────────────
def render_gst_module(user):
    st.markdown("""<div class="info-box">
    🔵 <b>GST Command Center</b> — Output tax, ITC offset, GSTR filing calendar & registration compliance.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">GST Entity Profile</div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        biz_name = st.text_input("Business / Trade Name", placeholder="e.g. KSP Enterprises")
        gstin    = st.text_input("GSTIN (if registered)", placeholder="36ABCDE1234F1Z5", max_chars=15)
    with g2:
        state    = st.selectbox("State", ["Telangana","Karnataka","Maharashtra","Tamil Nadu","Delhi","Gujarat","Other"])
        biz_type = st.selectbox("Category", ["Regular Taxpayer","Composition Dealer","E-Commerce","Export / SEZ","ISD"])
    with g3:
        itc_avail = st.number_input("ITC Available (₹)", min_value=0.0, step=100.0, format="%.2f")
        cash_paid = st.number_input("Cash Ledger Paid (₹)", min_value=0.0, step=100.0, format="%.2f")

    st.markdown('<div class="section-header">Supply Breakup by GST Rate</div>', unsafe_allow_html=True)
    r1,r2,r3,r4,r5,r6,r7 = st.columns(7)
    s0  = r1.number_input("0% Exempt", min_value=0.0, step=1000.0, format="%.2f")
    s5  = r2.number_input("5%",        min_value=0.0, step=1000.0, format="%.2f")
    s12 = r3.number_input("12%",       min_value=0.0, step=1000.0, format="%.2f")
    s18 = r4.number_input("18%",       min_value=0.0, step=1000.0, format="%.2f")
    s28 = r5.number_input("28%",       min_value=0.0, step=1000.0, format="%.2f")
    exp = r6.number_input("Export 0%", min_value=0.0, step=1000.0, format="%.2f")
    ext = r7.number_input("Pure Exempt",min_value=0.0,step=1000.0, format="%.2f")

    if st.button("📊  Compute GST Liability & Filing Calendar", use_container_width=True):
        if not biz_name:
            st.warning("⚠️ Enter business name."); return
        with st.spinner("Processing..."):
            gst = GSTEngine()
            result = gst.compute(itc_avail, cash_paid, exp, ext,
                                  {"0%":s0,"5%":s5,"12%":s12,"18%":s18,"28%":s28})
            st.session_state.last_gst_result = result
            pdf_bytes = generate_gst_pdf(biz_name, gstin or "UNREGISTERED", user["firm"], result)
            st.session_state.gst_pdf_bytes = pdf_bytes

        st.success(f"✅ GST computation complete for **{biz_name}**")
        gm1,gm2,gm3,gm4 = st.columns(4)
        gm1.metric("Annual Turnover", f"₹{result['annual_turnover']:,.0f}")
        gm2.metric("Gross Output Tax", f"₹{result['summary']['Gross Output Tax']:,.0f}")
        gm3.metric("Net GST Payable", f"₹{result['summary']['Net GST Payable']:,.0f}")
        gm4.metric("Cash Liability",  f"₹{result['summary']['Cash Ledger Requirement']:,.0f}")
        st.markdown("---")
        gt1,gt2,gt3 = st.tabs(["📋 Rate-wise Breakdown","📊 Summary","📅 Filing Calendar"])
        with gt1: st.json(result["rate_breakdown"])
        with gt2: st.json(result["summary"])
        with gt3: st.json(result["gstr_calendar"])

    if st.session_state.get("gst_pdf_bytes"):
        st.markdown("---")
        st.download_button("📥  Download GST Report (PDF)",
            data=st.session_state.gst_pdf_bytes,
            file_name=f"KSP_GST_{gstin or 'UNREG'}.pdf",
            mime="application/pdf", use_container_width=True)


# ─────────────────────────────────────────────
#  MODULE: KSP AI COMPLIANCE AGENT
#  (Standalone — for custom queries)
# ─────────────────────────────────────────────
def render_ai_agent_module(user):
    st.markdown("""<div class="info-box">
    🌐 <b>KSP AI Compliance & Filing Agent</b> — Powered by Google Gemini.<br/>
    Ask any compliance question, or use the ITR Engine above for automatic dual-report generation.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Client Context</div>', unsafe_allow_html=True)
    ac1, ac2 = st.columns(2)
    with ac1:
        client_name   = st.text_input("Client Name", placeholder="Dixith Chakravarthula")
        profile_model = st.selectbox("Profile", [
            "Traditional Professional / Priest (Dakshina & Pooja Inflows)",
            "Salaried Professional", "Freelancer / Consultant",
            "Small Retailer", "Investor", "NRI"
        ])
    with ac2:
        gross_ctx  = st.number_input("Gross Receipts (context, ₹)", min_value=0.0, step=1000.0, format="%.2f")
        regime_sel = st.selectbox("Regime", ["NEW Regime (Sec 115BAC)", "OLD Regime"])

    # ── Show last ITR result if available ─────
    if st.session_state.last_itr_result and st.checkbox("📎 Attach last computed ITR data as context"):
        r = st.session_state.last_itr_result
        st.markdown(f"""<div class="ksp-card ksp-card-accent" style="font-size:0.8rem;">
        <b>Attached ITR Context:</b> Form {r['assigned_form']} | GTI ₹{r['metrics']['Gross Total Income (GTI)']:,.2f} |
        Net Tax ₹{r['tax_breakdown']['NET TAX PAYABLE']:,.2f} | Regime {r['regime']}
        </div>""", unsafe_allow_html=True)
        attached_ctx = json.dumps({
            "itr_form": r["assigned_form"],
            "gti": r["metrics"]["Gross Total Income (GTI)"],
            "net_tax": r["tax_breakdown"]["NET TAX PAYABLE"],
            "regime": r["regime"]
        })
    else:
        attached_ctx = f"Gross Receipts: ₹{gross_ctx:,.2f}" if gross_ctx > 0 else "None"

    st.markdown('<div class="section-header">Compliance Query</div>', unsafe_allow_html=True)
    user_prompt = st.text_area(
        "Enter directive or question:",
        height=130,
        placeholder="e.g. Perform parallel computing for both Standard Compliance and Credit Optimization for this client. Show exact tax savings and recommended regime."
    )

    if st.button("⚡  Execute KSP AI Analysis", use_container_width=True):
        if not user_prompt.strip():
            st.warning("⚠️ Enter a query."); return
        context_block = f"\nClient: {client_name or 'Unknown'} | Profile: {profile_model} | Regime: {regime_sel}\nFinancial context: {attached_ctx}\n"
        with st.spinner("KSP AI processing..."):
            response = call_gemini(KSP_SYSTEM_PROMPT, context_block + user_prompt, max_tokens=2000)
        st.markdown(f"""<div class="ksp-card ksp-card-success">
        {response}
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MODULE: INCORPORATION MATRIX
# ─────────────────────────────────────────────
def render_incorporation_module(user):
    st.markdown("""<div class="info-box">
    📋 <b>Business Incorporation Strategy Matrix</b> — Pvt Ltd, LLP, OPC, Sole Prop, Partnership
    compared across tax, compliance, liability & cost.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Entity Parameters</div>', unsafe_allow_html=True)
    i1, i2, i3 = st.columns(3)
    with i1:
        promoters = st.number_input("No. of Promoters", min_value=1, max_value=200, value=2)
        revenue   = st.number_input("Projected Revenue (₹)", min_value=0.0, step=100000.0, format="%.0f")
    with i2:
        fdi       = st.checkbox("Requires FDI")
        ipo       = st.checkbox("IPO Plans")
        vc        = st.checkbox("Seeking VC / Angel Funding")
    with i3:
        sector    = st.selectbox("Sector", ["IT / Software","Manufacturing","Trading","Professional Services","E-Commerce","Healthcare","Other"])
        state_r   = st.selectbox("State", ["Telangana","Karnataka","Maharashtra","Delhi","Tamil Nadu","Other"])

    if st.button("📊  Generate Incorporation Matrix", use_container_width=True):
        entities = {
            "Private Limited Company": {"Tax Rate":"22% (115BAA) + Surcharge + 4% Cess",
                "Liability":"Limited","Compliance":"HIGH — ROC, Board meetings, Statutory audit",
                "FDI":"YES ✅","Min Capital":"Nil (post-2015)","Best For":"VC/FDI/IPO, 2+ founders",
                "Annual Cost":"₹40,000–₹1,20,000"},
            "LLP": {"Tax Rate":"30% + 4% Cess","Liability":"Limited",
                "Compliance":"MEDIUM — Annual return + accounts","FDI":"Limited",
                "Min Capital":"Nil","Best For":"Professional firms, 2+ partners",
                "Annual Cost":"₹15,000–₹40,000"},
            "One Person Company (OPC)": {"Tax Rate":"22% + Surcharge + 4% Cess",
                "Liability":"Limited","Compliance":"MEDIUM","FDI":"NO",
                "Min Capital":"Nil","Best For":"Solo founder, revenue < ₹2Cr",
                "Annual Cost":"₹20,000–₹50,000"},
            "Sole Proprietorship": {"Tax Rate":"Individual slabs (up to 30%)",
                "Liability":"UNLIMITED","Compliance":"LOW — ITR-3/4, GST if applicable",
                "FDI":"NO","Min Capital":"None","Best For":"Very small, single person",
                "Annual Cost":"₹5,000–₹15,000"},
            "Partnership Firm": {"Tax Rate":"30% + 4% Cess",
                "Liability":"UNLIMITED","Compliance":"LOW-MEDIUM",
                "FDI":"NO","Min Capital":"None","Best For":"Family business, traditional trade",
                "Annual Cost":"₹10,000–₹25,000"},
        }
        for entity, d in entities.items():
            with st.expander(f"🏢 {entity}"):
                cols = st.columns(2)
                for j,(k,v) in enumerate(d.items()):
                    cols[j%2].markdown(f"**{k}:** {v}")

        if fdi or vc or ipo:
            st.markdown("""<div class="ksp-card ksp-card-warning">
            ⭐ <b>Recommended: Private Limited Company</b> — Only structure supporting FDI/VC/IPO.
            Register under Companies Act 2013 via MCA portal.
            </div>""", unsafe_allow_html=True)
        elif promoters == 1:
            st.markdown("""<div class="ksp-card ksp-card-accent">
            ⭐ <b>Recommended: OPC</b> — Corporate liability shield for solo founder.
            If revenue < ₹40L, Sole Proprietorship + ITR-4 (44AD) is simpler.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="ksp-card ksp-card-success">
            ⭐ <b>Recommended: LLP</b> — Best balance of liability protection and compliance cost
            for professional services with multiple partners.
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MODULE: PREDICTIVE CFO MODELING
# ─────────────────────────────────────────────
def render_cfo_module(user):
    st.markdown("""<div class="info-box">
    📈 <b>Predictive Fractional CFO Modeling</b> — Advance tax schedule, Sec 208/234 planning,
    cashflow projection for AY 2026-27.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Income Projection</div>', unsafe_allow_html=True)
    p1,p2,p3 = st.columns(3)
    with p1:
        proj_rev  = st.number_input("Projected Revenue (₹)", min_value=0.0, step=50000.0, format="%.0f", value=2500000.0)
        proj_exp  = st.number_input("Business Expenses (₹)", min_value=0.0, step=10000.0, format="%.0f", value=800000.0)
    with p2:
        proj_sal  = st.number_input("Salary / Fixed Income (₹)", min_value=0.0, step=10000.0, format="%.0f")
        proj_cg   = st.number_input("Expected Capital Gains (₹)", min_value=0.0, step=10000.0, format="%.0f")
    with p3:
        tds_ded   = st.number_input("TDS Already Deducted (₹)", min_value=0.0, step=1000.0, format="%.0f")
        adv_paid  = st.number_input("Advance Tax Paid (₹)", min_value=0.0, step=1000.0, format="%.0f")

    if st.button("📈  Generate Advance Tax Schedule", use_container_width=True):
        net = max(0, proj_rev - proj_exp + proj_sal + proj_cg)
        if net<=400000: tax=0
        elif net<=800000: tax=(net-400000)*0.05
        elif net<=1200000: tax=20000+(net-800000)*0.10
        elif net<=1600000: tax=60000+(net-1200000)*0.15
        elif net<=2000000: tax=120000+(net-1600000)*0.20
        else: tax=200000+(net-2000000)*0.30
        tax_cess = tax * 1.04
        balance  = max(0, tax_cess - tds_ded - adv_paid)

        installments = {
            "1st — by 15 Jun 2025": max(0, tax_cess*0.15),
            "2nd — by 15 Sep 2025": max(0, tax_cess*0.45 - tax_cess*0.15),
            "3rd — by 15 Dec 2025": max(0, tax_cess*0.75 - tax_cess*0.45),
            "4th — by 15 Mar 2026": max(0, tax_cess - tax_cess*0.75),
        }
        am1,am2,am3,am4 = st.columns(4)
        am1.metric("Net Income",         f"₹{net:,.0f}")
        am2.metric("Est. Tax (with cess)",f"₹{tax_cess:,.0f}")
        am3.metric("TDS + Advance Paid", f"₹{tds_ded+adv_paid:,.0f}")
        am4.metric("Balance Due",        f"₹{balance:,.0f}")

        st.markdown('<div class="section-header">Advance Tax Installment Schedule (Sec 208)</div>',
                    unsafe_allow_html=True)
        for inst, amt in installments.items():
            ca, cb = st.columns([3,1])
            ca.markdown(f"**{inst}**")
            cb.markdown(f"₹ {amt:,.0f}")

        if balance > 10_000:
            st.markdown(f"""<div class="ksp-card ksp-card-warning">
            ⚠️ <b>Action Required:</b> ₹{balance:,.0f} balance payable.
            Non-payment attracts interest under Sec 234B (1%/month) and Sec 234C (1%/month per shortfall).
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="ksp-card ksp-card-success">
            ✅ TDS + advance payments appear sufficient. Verify at year-end with actual P&L.
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar(user):
    with st.sidebar:
        st.markdown("""<div style="padding:0.75rem 0;border-bottom:1px solid #30363D;margin-bottom:1rem;">
        <div style="font-family:'IBM Plex Mono';font-size:1rem;font-weight:700;color:#58A6FF;">⚙️ KSP CONSOLE</div>
        <div style="font-size:0.72rem;color:#8B949E;margin-top:2px;">PLATFORM v3.0</div>
        </div>""", unsafe_allow_html=True)

        modules = [
            ("itr",   "🚀 Smart ITR Engine + AI Dual Report"),
            ("gst",   "🔵 GST Command Center"),
            ("ai",    "🌐 KSP AI Compliance Agent"),
            ("incorp","📋 Incorporation Strategy Matrix"),
            ("cfo",   "📈 Predictive CFO Modeling"),
        ]
        st.markdown('<div style="font-size:0.7rem;color:#8B949E;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem;">Select Module:</div>',
                    unsafe_allow_html=True)
        for key, label in modules:
            if has_module_access(user["modules"], key):
                if st.button(label, key=f"mod_{key}", use_container_width=True):
                    st.session_state.active_module = key
                    st.rerun()
            else:
                st.markdown(f'<div style="color:#484F58;font-size:0.82rem;padding:0.3rem 0;">🔒 {label}</div>',
                            unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"""<div style="font-size:0.72rem;color:#8B949E;line-height:1.8;">
        <b style="color:#C9D1D9;">Firm:</b> {user['firm']}<br/>
        <b style="color:#C9D1D9;">Plan:</b> <span style="color:#3FB950;">{user['plan']}</span><br/>
        <b style="color:#C9D1D9;">User:</b> {user['username']}<br/>
        <b style="color:#C9D1D9;">AY:</b> 2026-27 | Bank: Universal Parser v3
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div style="font-size:0.7rem;color:#3FB950;">🔒 Security Mode: Active</div>',
                    unsafe_allow_html=True)
        st.markdown("")
        if st.button("⎋  Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ─────────────────────────────────────────────
#  MAIN CONTROLLER
# ─────────────────────────────────────────────
def render_main(user):
    render_sidebar(user)
    titles = {
        "itr":   ("🚀","Smart ITR Filing Engine + AI Dual Report","Parse any bank · New & Old Regime · Standard + Credit Optimized PDF"),
        "gst":   ("🔵","GST Command Center","Output Tax · ITC · GSTR Calendar · Registration"),
        "ai":    ("🌐","KSP AI Compliance Agent","Google Gemini · Natural language · AIS / ITR / GST queries"),
        "incorp":("📋","Incorporation Strategy Matrix","Pvt Ltd · LLP · OPC · Partnership · Proprietorship"),
        "cfo":   ("📈","Predictive CFO Modeling","Advance Tax · Sec 208/234 · Cashflow Forecast"),
    }
    mod = st.session_state.active_module
    icon, title, subtitle = titles.get(mod, ("⚙️","Module",""))
    st.markdown(f"""<div class="brand-bar">
    <div class="logo">{icon}</div>
    <div><div class="title">{title}</div><div class="subtitle">{subtitle}</div></div>
    <div class="status-badge">● LIVE</div>
    </div>""", unsafe_allow_html=True)

    if mod == "itr":    render_itr_module(user)
    elif mod == "gst":  render_gst_module(user)
    elif mod == "ai":   render_ai_agent_module(user)
    elif mod == "incorp": render_incorporation_module(user)
    elif mod == "cfo":  render_cfo_module(user)


# ─────────────────────────────────────────────
#  ENTRYPOINT
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    render_login()
else:
    render_main(st.session_state.user)
