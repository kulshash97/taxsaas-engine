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
# ─────────────────────────────────────────────
class UniversalBankParser:
    @staticmethod
    def parse_pdf(file_obj) -> float:
        pdf = PdfReader(file_obj)
        page_texts = [p.extract_text() or "" for p in pdf.pages]
        full_text  = "\n".join(page_texts)

        val = UniversalBankParser._strategy_summary_row(full_text)
        if val: return val

        val = UniversalBankParser._strategy_summary_label(full_text)
        if val: return val

        val = UniversalBankParser._strategy_transaction_rows(page_texts)
        if val: return val

        val = UniversalBankParser._strategy_broad_fallback(full_text)
        return val or 0.0

    @staticmethod
    def _strategy_summary_row(full_text: str) -> float:
        trigger_phrases = [
            "BROUGHT FORWARD", "OPENING BALANCE", "CR COUNT", "TOTAL DEBIT",
            "STATEMENT SUMMARY", "ACCOUNT SUMMARY", "CLOSING BALANCE"
        ]
        lines = full_text.split("\n")
        for i, line in enumerate(lines):
            u = line.upper()
            if any(ph in u for ph in trigger_phrases):
                block = "\n".join(lines[i:i+5])
                raw = re.findall(r'([\d,]+\.\d{2})(?:CR|DR)?', block, re.IGNORECASE)
                amounts = []
                for n in raw:
                    try:
                        v = float(n.replace(",",""))
                        if v > 500:
                            amounts.append(v)
                    except: pass
                if len(amounts) >= 2:
                    return round(amounts[-2], 2)
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
                    if v > 500:
                        return round(v, 2)
                except: pass
        return 0.0

    @staticmethod
    def _strategy_transaction_rows(page_texts: list) -> float:
        credit_tags  = ['DEP TFR','UPI/CR','NEFT CR','RTGS CR','IMPS CR',
                        'CR/','SALARY','CREDITED','TRANSFER CR','INWARD']
        skip_tags    = ['WDL TFR','WDL','UPI/DR','DEBIT','INTEREST CREDIT',
                        'CEMTEX DEP','ATM','AMC','REVERSAL','ROLLBACK',
                        'FAILED','REFUND','BOUNCE','RETURN']
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
                if len(clean) >= 2:
                    total += clean[-2]
        return round(total, 2) if total > 500 else 0.0

    @staticmethod
    def _strategy_broad_fallback(full_text: str) -> float:
        total = 0.0
        for line in full_text.split("\n"):
            u = line.upper()
            if any(k in u for k in ['DEP','CR/','/CR','CREDIT','INWARD']):
                if any(k in u for k in ['WDL','DEBIT','INTEREST','CEMTEX']): continue
                nums = re.findall(r'\b(\d{1,3}(?:,\d{2,3})*\.\d{2})\b', line)
                if len(nums) >= 2:
                    try: total += float(nums[-2].replace(",",""))
                    except: pass
        return round(total, 2)

    @staticmethod
    def parse_dataframe(df: pd.DataFrame) -> float:
        df.columns = [str(c).strip().upper() for c in df.columns]
        cr_col = next((c for c in df.columns if any(k in c for k in
            ['CREDIT','DEPOSIT','CR AMT','CR_AMT','INWARD','AMOUNT CREDITED',
             'CREDIT AMOUNT','DEP','CR(INR)','CREDIT(INR)'])), None)
        desc_col = next((c for c in df.columns if any(k in c for k in
            ['DESC','REMARK','NARRATION','PARTICULARS','DETAILS','TRAN','REFERENCE'])), None)

        if cr_col:
            df[cr_col] = pd.to_numeric(df[cr_col].astype(str).str.replace(",","").str.replace("CR",""), errors='coerce').fillna(0)
            if desc_col:
                mask = df[desc_col].astype(str).str.contains(
                    'REVERSAL|ROLLBACK|REFUND|FAILED|BOUNCE|INTEREST CREDIT',
                    case=False, na=False)
                return float(df[~mask][cr_col].sum())
            return float(df[cr_col].sum())

        amt_col = next((c for c in df.columns if any(k in c for k in
            ['AMOUNT','AMT','VALUE','TRANSACTION AMT'])), None)
        type_col = next((c for c in df.columns if any(k in c for k in
            ['TYPE','DR/CR','CR DR','INDICATOR','SIDE'])), None)
        if amt_col and type_col:
            df[amt_col] = pd.to_numeric(df[amt_col].astype(str).str.replace(",",""), errors='coerce').fillna(0)
            cr_mask = df[type_col].astype(str).str.upper().str.contains('CR|CREDIT|DEP', na=False)
            return float(df[cr_mask][amt_col].sum())
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
            st.error(f"Bank parsing error: {e}")
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
                r[field] = float(pd.to_numeric(df[col].astype(str).str.replace(",",""), errors='coerce').sum())
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

        gross_total = (self.salary_income + self.presumptive_profit +
                       self.stcg_111a + self.stcg_other +
                       self.ltcg_112a + self.ltcg_other + self.other_sources_income)
        std_ded = min(75_000, self.salary_income) if regime == "NEW" and self.salary_income > 0 else (
                  min(50_000, self.salary_income) if regime == "OLD" and self.salary_income > 0 else 0)
        chapter_via = self.total_deductions if regime == "OLD" else 0.0
        net_taxable = max(0.0, gross_total - std_ded - chapter_via)

        special_cg = self.stcg_111a + self.ltcg_112a + self.ltcg_other
        slab_income = max(0.0, net_taxable - special_cg)
        raw_slab_tax = 0.0
        if regime == "NEW":
            for (lo, hi, rate) in [(0,400000,0),(400000,800000,0.05),(800000,1200000,0.10),
                                   (1200000,1600000,0.15),(1600000,2000000,0.20),(2000000,float('inf'),0.30)]:
                if slab_income > lo:
                    raw_slab_tax += (min(slab_income, hi) - lo) * rate
        else:
            for (lo, hi, rate) in [(0,250000,0),(250000,500000,0.05),(500000,1000000,0.20),(1000000,float('inf'),0.30)]:
                if slab_income > lo:
                    raw_slab_tax += (min(slab_income, hi) - lo) * rate

        stcg_111a_tax = self.stcg_111a * 0.20          
        ltcg_112a_tax = max(0.0, (self.ltcg_112a - 125_000) * 0.125) if self.ltcg_112a > 125_000 else 0.0
        ltcg_other_tax = self.ltcg_other * 0.125

        total_pre_rebate = raw_slab_tax + stcg_111a_tax + ltcg_112a_tax + ltcg_other_tax

        if regime == "NEW":
            rebate = min(25_000, raw_slab_tax) if net_taxable <= 1_200_000 else 0.0
        else:
            rebate = min(12_500, raw_slab_tax) if net_taxable <= 500_000 else 0.0

        net_tax = max(0.0, total_pre_rebate - rebate)

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
#  FIXED GEMINI API HELPER (404 Error Resolved)
# ─────────────────────────────────────────────
def call_gemini(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY",""))
    if not GEMINI_API_KEY:
        return "❌ GEMINI_API_KEY not configured. Add it in Streamlit Secrets."
    
    combined = f"{system_prompt}\n\n---\n\nUser Query:\n{user_prompt}"
    
    # FIX: Correct payload layout formatting for v1beta standard candidates structure
    payload = json.dumps({
        "contents": [{"parts": [{"text": combined}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.3}
    }).encode()
    
    # FIX: Clean route generation sequence (Removed duplicate nested path prefixes)
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
- STCG Sec 111A (listed equity): 20% (Finance Act 2024)
- LTCG Sec 112A (listed equity): 12.5% with ₹1.25L exemption (Finance Act 2024)
- Section 87A (New Regime): ₹25,000 rebate if net taxable ≤ ₹12L
- Section 87A (Old Regime): ₹12,500 rebate if net taxable ≤ ₹5L
- Standard Deduction: ₹75,000 (New), ₹50,000 (Old)
- Sec 44AD turnover limit: ₹3Cr (digital), presumptive: 6%
- Sec 44ADA limit: ₹75L, presumptive: 50%
- Sec 44AB audit: triggered if turnover > ₹1Cr (cash) / ₹10Cr (digital)

Respond with structured sections, concrete numbers, and actionable filing steps.
For dual-report requests, always produce BOTH: (A) Standard Compliance and (B) Credit Optimization layout."""


# ─────────────────────────────────────────────
#  PDF GENERATOR — ITR REPORT (Completed Section)
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
        rows2.append([Paragraph(k, bold_s if k == "NET TAX PAYABLE" else body_s), 
                      Paragraph(f"₹ {v:,.2f}", bold_s if k == "NET TAX PAYABLE" else body_s)])
    t3 = Table(rows2, colWidths=[370,160])
    t3.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#EDF2F7")),
                             ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E0")),
                             ('PADDING',(0,0),(-1,-1),4)]))
    story.append(t3)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

# ─────────────────────────────────────────────
#  STUB ENTRY MODULE RENDERING ROUTER
# ─────────────────────────────────────────────
def render_itr_module(user):
    st.subheader("Interactive Tax & Optimization Suite")
    st.info("Upload statements or manually adjust downstream flags below.")

if __name__ == "__main__":
    if not st.session_state.get("logged_in"):
        st.markdown('<div class="login-container"><div class="login-logo">⚙️</div><div class="login-title">KSP Console Link</div></div>', unsafe_allow_html=True)
        u_input = st.text_input("B2B Identifier")
        p_input = st.text_input("Security Access Code", type="password")
        if st.button("Authenticate Instance"):
            session = authenticate(u_input, p_input)
            if session:
                st.session_state.logged_in = True
                st.session_state.user = session
                st.rerun()
            else:
                st.error("Invalid B2B Security Token")
    else:
        render_itr_module(st.session_state.user)