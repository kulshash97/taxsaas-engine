"""
KSP CONSOLE PLATFORM — TaxSaaS B2B Engine v4.1 (Enterprise Production Build)
Kulkarni Strategic Partners | Assessment Year (AY) 2026-27
- Variable-Layout Bank Statement Parser (Refined Credit Matching Strategy)
- Dedicated KSP Structural Profile Report Parser
- Advanced AIS / TIS Unified XML/PDF Parsing Layer
- Capital Gains Engine (Finance Act 2024 / Budget 2025 Slabs)
- Interactive Compliance Workspace for Online Portal Mode Data Filing
"""

import os
import io
import re
import json
import time
import pandas as pd
import numpy as np
import streamlit as st
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
#  PAGE STRUCTURAL CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KSP Console Platform", 
    page_icon="⚙️",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────────────────────
#  GLOBAL ENTERPRISE UI STYLING
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; background-color: #0D1117; color: #E2E8F0; }
section[data-testid="stSidebar"] { background: #161B22!important; border-right: 1px solid #30363D; }
section[data-testid="stSidebar"] * { color: #C9D1D9!important; }
.main .block-container { padding-top: 1.5rem; }
.ksp-card { background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; }
.ksp-card-accent { border-left: 3px solid #58A6FF; }
.ksp-card-success { border-left: 3px solid #3FB950; }
[data-testid="metric-container"] { background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 0.75rem 1rem; }
[data-testid="metric-container"] label { color: #8B949E!important; font-size: 0.75rem!important; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #58A6FF!important; font-family: 'IBM Plex Mono'!important; font-size: 1.35rem!important; font-weight: 600; }
.stButton>button { background: #238636!important; color: #FFFFFF!important; border: 1px solid #2EA043!important; border-radius: 6px!important; font-family: 'IBM Plex Sans'!important; font-weight: 600!important; padding: 0.5rem 1.25rem!important; width: 100%; }
.stButton>button:hover { background: #2EA043!important; box-shadow: 0 0 10px rgba(46,160,67,0.4)!important; }
.stTextInput>div>div>input, .stTextArea textarea { background: #0D1117!important; border: 1px solid #30363D!important; border-radius: 6px!important; color: #E2E8F0!important; font-family: 'IBM Plex Mono'!important; }
.stSelectbox>div>div { background: #0D1117!important; border: 1px solid #30363D!important; color: #E2E8F0!important; }
.brand-bar { display: flex; align-items: center; gap: 12px; padding: 0.6rem 0; border-bottom: 1px solid #30363D; margin-bottom: 1.5rem; }
.brand-bar .title { font-family: 'IBM Plex Mono'; font-size: 1.1rem; font-weight: 600; color: #58A6FF; letter-spacing: 0.05em; }
.brand-bar .subtitle { font-size: 0.75rem; color: #8B949E; }
.status-badge { margin-left: auto; background: #0D2818; border: 1px solid #3FB950; color: #3FB950; border-radius: 12px; padding: 2px 10px; font-size: 0.72rem; font-family: 'IBM Plex Mono'; }
.portal-field { background: #21262D; border: 1px solid #30363D; padding: 4px 8px; border-radius: 4px; font-family: 'IBM Plex Mono'; font-size: 0.9rem; color: #58A6FF; font-weight: 600; display: inline-block; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
#  B2B AUTHENTICATION CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
B2B_USERS = {
    "admin": ("KSP@2026#Admin", "Kulkarni Strategic Partners", "ENTERPRISE", "all"),
    "ca_shashank": ("Shashank@KSP1", "Shashank Kulkarni & Associates", "PRO", "all")
}

def authenticate(username, password):
    u = B2B_USERS.get(username.lower().strip())
    if u and u[0] == password:
        return {"username": username, "firm": u[1], "plan": u[2], "modules": u[3]}
    return None

# ──────────────────────────────────────────────────────────────────────────────
#  STATE INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.active_module = "itr"
    st.session_state.parsed_gross = 0.0
    st.session_state.parsed_salary = 0.0
    st.session_state.parsed_other_source = 0.0
    st.session_state.parsed_stcg_111a = 0.0
    st.session_state.parsed_stcg_other = 0.0
    st.session_state.parsed_ltcg_112a = 0.0
    st.session_state.parsed_ltcg_other = 0.0
    st.session_state.pan_number = "NOT DETECTED"
    st.session_state.assessee_name = "UNKNOWN CLIENT"
    st.session_state.consolidated_pdf_ready = False
    st.session_state.consolidated_pdf_bytes = None

# ──────────────────────────────────────────────────────────────────────────────
#  NEW: KSP PROFILE STRUCTURAL PARSER
# ──────────────────────────────────────────────────────────────────────────────
class KSPProfileParser:
    """
    Parses exact structured text profiles from a previously compiled 
    KSP Consolidated Report PDF to retrieve already processed totals cleanly.
    """
    @staticmethod
    def parse_profile(file_obj) -> dict:
        result = {"gross_receipts": 0.0, "salary": 0.0, "other_source": 0.0, "stcg_111a": 0.0, "ltcg_112a": 0.0}
        try:
            pdf = PdfReader(file_obj)
            full_text = "\n".join([p.extract_text() or "" for p in pdf.pages])
            
            biz_m = re.search(r'Business Gross Receipts / Banking Turnover Credit\s+([\d,]+\.\d{2})', full_text)
            if biz_m: result["gross_receipts"] = float(biz_m.group(1).replace(",", ""))
                
            sal_m = re.search(r'Salary Income Records \(as per AIS/TIS\)\s+([\d,]+\.\d{2})', full_text)
            if sal_m: result["salary"] = float(sal_m.group(1).replace(",", ""))

            os_m = re.search(r'Income from Other Sources [^\d]*?([\d,]+\.\d{2})', full_text)
            if os_m: result["other_source"] = float(os_m.group(1).replace(",", ""))

            stcg_m = re.search(r'Short Term Capital Gains \(Sec 111A[^\d]*?([\d,]+\.\d{2})', full_text)
            if stcg_m: result["stcg_111a"] = float(stcg_m.group(1).replace(",", ""))

            ltcg_m = re.search(r'Long Term Capital Gains \(Sec 112A[^\d]*?([\d,]+\.\d{2})', full_text)
            if ltcg_m: result["ltcg_112a"] = float(ltcg_m.group(1).replace(",", ""))
        except Exception as e:
            st.error(f"KSP Report parsing context exception: {e}")
        return result

# ──────────────────────────────────────────────────────────────────────────────
#  REFINED UNIVERSAL BANK STATEMENT PARSER
# ──────────────────────────────────────────────────────────────────────────────
class UniversalBankParser:
    @staticmethod
    def parse(file_obj) -> float:
        if not file_obj: return 0.0
        name = file_obj.name.lower()
        
        if name.endswith('.pdf'):
            return UniversalBankParser._parse_pdf(file_obj)
        elif name.endswith(('.xlsx', '.xls')):
            return UniversalBankParser._parse_dataframe(pd.read_excel(file_obj, engine='openpyxl'))
        elif name.endswith('.csv'):
            file_obj.seek(0)
            return UniversalBankParser._parse_dataframe(pd.read_csv(file_obj, encoding='latin-1'))
        return 0.0

    @staticmethod
    def _parse_pdf(file_obj) -> float:
        reader = PdfReader(file_obj)
        full_text = "\n".join([p.extract_text() or "" for p in reader.pages])

        # Match structural summary totals first
        summary_labels = [
            r'Total\s+Cr(?:edit)?s?\s*[\(₹:)]*\s*([\d,]+\.\d{2})',
            r'(?:Sum|Total)\s+of\s+Credits?\s*:?\s*([\d,]+\.\d{2})',
            r'Total\s+Amount\s+Credited\s*:?\s*([\d,]+\.\d{2})'
        ]
        for pat in summary_labels:
            match = re.search(pat, full_text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(",", ""))

        # Line fallback scanning algorithm
        running_credits = 0.0
        ignore_patterns = re.compile(r'REVERSAL|ROLLBACK|REFUND|FAILED|BOUNCE|SWEEP|CONTRA', re.IGNORECASE)
        
        for line in full_text.split('\n'):
            amounts = re.findall(r'\b\d{1,3}(?:,\d{2,3})*\.\d{2}\b', line)
            if not amounts: continue
            
            # Check if line looks like an account credit line or explicitly avoids DR triggers
            if "CR" in line.upper() or not any(dr in line.upper() for dr in ["WDL", "DEBIT", "UPI/DR"]):
                if not ignore_patterns.search(line):
                    try:
                        clean_amounts = [float(a.replace(",", "")) for a in amounts]
                        running_credits += clean_amounts[0]
                    except: pass
        return round(running_credits, 2)

    @staticmethod
    def _parse_dataframe(df: pd.DataFrame) -> float:
        df.columns = [str(c).strip().upper() for c in df.columns]
        cr_col = next((c for c in df.columns if any(k in c for k in ['CREDIT', 'DEPOSIT', 'CR AMT'])), None)
        if cr_col:
            return float(pd.to_numeric(df[cr_col].astype(str).str.replace(",", ""), errors='coerce').fillna(0).sum())
        return 0.0

# ──────────────────────────────────────────────────────────────────────────────
#  AIS / TIS PARSER LAYER
# ──────────────────────────────────────────────────────────────────────────────
class AISDocumentParser:
    @staticmethod
    def parse(file_obj) -> dict:
        summary = {"salary": 0.0, "other_source": 0.0, "pan": "NOT DETECTED"}
        if not file_obj: return summary
        try:
            full_text = "\n".join([p.extract_text() or "" for p in PdfReader(file_obj).pages])
            
            pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', full_text)
            if pan_match: summary["pan"] = pan_match.group(0)
            
            sal_blocks = re.findall(r'(?:Salary|Income\s+under\s+head\s+salary)[^\d]*?([\d,]+\.\d{2})', full_text, re.IGNORECASE)
            for val in sal_blocks:
                summary["salary"] = max(summary["salary"], float(val.replace(",", "")))
                
            os_patterns = [
                r'(?:Interest\s+from\s+savings\s+bank)[^\d]*?([\d,]+\.\d{2})',
                r'(?:Interest\s+from\s+deposit)[^\d]*?([\d,]+\.\d{2})',
                r'(?:Dividend\s+Income)[^\d]*?([\d,]+\.\d{2})'
            ]
            for pat in os_patterns:
                for match in re.findall(pat, full_text, re.IGNORECASE):
                    summary["other_source"] += float(match.replace(",", ""))
        except Exception as e:
            st.error(f"AIS line extraction failure: {e}")
        return summary

# ──────────────────────────────────────────────────────────────────────────────
#  TAX LIABILITY CALCULATOR ENGINE (AY 2026-27 COMPLIANT)
# ──────────────────────────────────────────────────────────────────────────────
class RobustTaxEngine:
    def __init__(self):
        self.turnover = 0.0
        self.salary = 0.0
        self.other_source = 0.0
        self.stcg_111a = 0.0
        self.ltcg_112a = 0.0

    def compute(self, regime: str) -> dict:
        presumptive_profit = round(self.turnover * 0.06, 2) if self.turnover > 0 else 0.0
        std_deduction = 75000.0 if regime == "NEW" and self.salary > 0 else (50000.0 if regime == "OLD" and self.salary > 0 else 0.0)
        
        net_slab_income = max(0.0, self.salary - std_deduction) + presumptive_profit + self.other_source
        net_taxable = net_slab_income + self.stcg_111a + self.ltcg_112a
        
        # Slabs calculation matrix
        raw_slab_tax = 0.0
        if regime == "NEW":
            slabs = [(0, 400000, 0.0), (400000, 800000, 0.05), (800000, 1200000, 0.10),
                     (1200000, 1600000, 0.15), (1600000, 2000000, 0.20), (2000000, float('inf'), 0.30)]
        else:
            slabs = [(0, 250000, 0.0), (250000, 500000, 0.05), (500000, 1000000, 0.20), (1000000, float('inf'), 0.30)]

        for lo, hi, rate in slabs:
            if net_slab_income > lo:
                raw_slab_tax += (min(net_slab_income, hi) - lo) * rate

        tax_stcg = self.stcg_111a * 0.20
        tax_ltcg = max(0.0, (self.ltcg_112a - 125000) * 0.125)
        
        total_pre_rebate = raw_slab_tax + tax_stcg + tax_ltcg
        
        rebate = 0.0
        if regime == "NEW" and net_taxable <= 1200000.0:
            rebate = min(25000.0, total_pre_rebate)
        elif regime == "OLD" and net_taxable <= 500000.0:
            rebate = min(12500.0, raw_slab_tax)
            
        post_rebate = max(0.0, total_pre_rebate - rebate)
        cess = post_rebate * 0.04
        
        return {
            "net_taxable": net_taxable,
            "slab_tax": raw_slab_tax,
            "stcg_tax": tax_stcg,
            "ltcg_tax": tax_ltcg,
            "rebate": rebate,
            "cess": cess,
            "net_payable": round(post_rebate + cess, 2)
        }

# ──────────────────────────────────────────────────────────────────────────────
#  PDF COMPILED GENERATOR TOOL
# ──────────────────────────────────────────────────────────────────────────────
def generate_consolidated_compliance_pdf() -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1A365D")
    story = [
        Paragraph("KULKARNI STRATEGIC PARTNERS — CONSOLIDATED TAX REPORT", ParagraphStyle('T', parent=styles['Heading1'], fontSize=14, textColor=c_primary)),
        Spacer(1, 15)
    ]
    
    fin_data = [
        ["Income Stream Data Type Source Head", "Extracted Value Amount (INR)"],
        ["Business Gross Receipts / Banking Turnover Credit", f"{st.session_state.parsed_gross:,.2f}"],
        ["Salary Income Records (as per AIS/TIS)", f"{st.session_state.parsed_salary:,.2f}"],
        ["Income from Other Sources (Savings / Deposits)", f"{st.session_state.parsed_other_source:,.2f}"],
        ["Short Term Capital Gains (Sec 111A - Equity Trading)", f"{st.session_state.parsed_stcg_111a:,.2f}"],
        ["Long Term Capital Gains (Sec 112A - Equity Holdings)", f"{st.session_state.parsed_ltcg_112a:,.2f}"]
    ]
    t = Table(fin_data, colWidths=[340, 180])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t)
    
    doc.build(story)
    return buffer.getvalue()

# ──────────────────────────────────────────────────────────────────────────────
#  STREAMLIT INTERFACE RENDERING LOGIC
# ──────────────────────────────────────────────────────────────────────────────
def render_login():
    st.markdown('<div style="max-width:400px; margin:auto; padding:2rem; background:#161B22; border-radius:8px;">', unsafe_allow_html=True)
    st.subheader("KSP Console Platform Authorization Node")
    u = st.text_input("User UID")
    p = st.text_input("Security Secret Token Password", type="password")
    if st.button("Authenticate Login Connection"):
        session = authenticate(u, p)
        if session:
            st.session_state.logged_in = True
            st.session_state.user = session
            st.rerun()
        else:
            st.error("Invalid cryptographic tokens provided.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_itr_module():
    st.markdown("### Multi-Tenant Document Processing Node Hub Console Workspace")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<div class="ksp-card">', unsafe_allow_html=True)
        st.markdown("##### Ingest Raw Source Files")
        uploaded_doc = st.file_uploader("Upload Bank Statement OR KSP Consolidated PDF Report Document", type=["pdf", "csv", "xlsx"])
        uploaded_ais = st.file_uploader("Upload Official AIS/TIS Standard Summary File PDF", type=["pdf"])
        
        if st.button("Run Dynamic Extraction Framework"):
            if uploaded_doc:
                fname = uploaded_doc.name.lower()
                if "tax_profile" in fname or "consolidated" in fname:
                    profile = KSPProfileParser.parse_profile(uploaded_doc)
                    st.session_state.parsed_gross = profile["gross_receipts"]
                    st.session_state.parsed_salary = profile["salary"]
                    st.session_state.parsed_other_source = profile["other_source"]
                    st.session_state.parsed_stcg_111a = profile["stcg_111a"]
                    st.session_state.parsed_ltcg_112a = profile["ltcg_112a"]
                else:
                    st.session_state.parsed_gross = UniversalBankParser.parse(uploaded_doc)
                    
            if uploaded_ais:
                ais_data = AISDocumentParser.parse(uploaded_ais)
                st.session_state.parsed_salary = ais_data["salary"]
                st.session_state.parsed_other_source = ais_data["other_source"]
                st.session_state.pan_number = ais_data["pan"]
                
            st.session_state.consolidated_pdf_bytes = generate_consolidated_compliance_pdf()
            st.session_state.consolidated_pdf_ready = True
            st.success("Extraction engine execution finished successfully.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="ksp-card">', unsafe_allow_html=True)
        st.markdown("##### Manual Verification Fields Map Workspace")
        st.session_state.assessee_name = st.text_input("Client Legal Structural Name ID Mapping", value=st.session_state.assessee_name)
        st.session_state.parsed_gross = st.number_input("Extracted Turnovers / Total Base Inbound Receipts Ledger Amount", value=st.session_state.parsed_gross)
        st.session_state.parsed_salary = st.number_input("Extracted Salary Structural Components Amount", value=st.session_state.parsed_salary)
        st.session_state.parsed_other_source = st.number_input("Other Income Component Parameters Aggregate", value=st.session_state.parsed_other_source)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    engine = RobustTaxEngine()
    engine.turnover = st.session_state.parsed_gross
    engine.salary = st.session_state.parsed_salary
    engine.other_source = st.session_state.parsed_other_source
    engine.stcg_111a = st.session_state.parsed_stcg_111a
    engine.ltcg_112a = st.session_state.parsed_ltcg_112a
    
    res = engine.compute("NEW")
    
    st.markdown("##### Live Online Portal Submission Map Dashboard Matrix Fields View")
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        st.markdown(f"**BP Business Turnover Metric Input:** <div class='portal-field'>₹ {res['net_taxable']:,.2f}</div>", unsafe_allow_html=True)
    with pc2:
        st.markdown(f"**Schedule OS Head Entry Parameters:** <div class='portal-field'>₹ {engine.other_source:,.2f}</div>", unsafe_allow_html=True)
    with pc3:
        st.markdown(f"**NET PORTAL TAX LIABILITY:** <div class='portal-field' style='color:#3FB950;'>₹ {res['net_payable']:,.2f}</div>", unsafe_allow_html=True)

def main():
    if not st.session_state.logged_in:
        render_login()
    else:
        st.markdown(f'<div class="brand-bar"><div class="title">KSP CONSOLE PLATFORM v4.1</div><div class="status-badge">● NODE ACTIVE</div></div>', unsafe_allow_html=True)
        render_itr_module()

if __name__ == "__main__":
    main()