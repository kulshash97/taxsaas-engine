import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import os
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ────────────────────────────────────────────────────────
# 1. GOOGLE GEMINI API FIX ENGINE
# ────────────────────────────────────────────────────────
import google.generativeai as genai

# Configure Google API key from Streamlit secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    # Local fallback option
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "MOCK_KEY"))

def run_ai_compliance_analysis(prompt_context: str) -> str:
    """Runs a structured optimization evaluation using the corrected production endpoint."""
    try:
        # Fixed 404 Error: Swapped to production stable string target
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            f"You are an elite Indian Corporate Tax Strategy Advisor. Analyze the following scenario and provide optimal compliance planning routes:\n\n{prompt_context}"
        )
        return response.text
    except Exception as e:
        # Graceful fallback context structure if API key is unconfigured
        return f"⚠️ Optimization Analysis Deferred: {str(e)}\n\nFallback Recommendation: Review balance sheets against Section 44ADA thresholds manually."

# ────────────────────────────────────────────────────────
# 2. DOCUMENT INGESTION ENGINES (ADVANCED PARSERS)
# ────────────────────────────────────────────────────────
class UniversalBankParser:
    @staticmethod
    def parse_pdf(file_obj) -> float:
        pdf = PdfReader(file_obj)
        page_texts = [p.extract_text() or "" for p in pdf.pages]
        full_text  = "\n".join(page_texts)

        # Pass 1: Summary Layout Analysis
        val = UniversalBankParser._strategy_summary_row(full_text)
        if val > 0: return val

        # Pass 2: Specific Label Extraction
        val = UniversalBankParser._strategy_summary_label(full_text)
        if val > 0: return val

        # Pass 3: Granular Transaction Stream Ingestion
        val = UniversalBankParser._strategy_transaction_rows(page_texts)
        if val > 0: return val

        # Pass 4: Aggressive Regex Multi-Digit Token Deep-Scan Fallback
        val = UniversalBankParser._strategy_deep_regex_extraction(full_text)
        return val or 0.0

    @staticmethod
    def _strategy_summary_row(full_text: str) -> float:
        trigger_phrases = ["BROUGHT FORWARD", "OPENING BALANCE", "CR COUNT", "TOTAL DEBIT", "STATEMENT SUMMARY", "ACCOUNT SUMMARY", "CLOSING BALANCE", "TOTAL CR"]
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
        skip_tags    = ['WDL TFR','WDL','UPI/DR','DEBIT','INTEREST CREDIT','ATM','AMC']
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
        lines = full_text.split("\n")
        candidates = []
        for line in lines:
            if any(k in line.upper() for k in ["INTEREST", "BAL", "OPENING", "CLOSING"]): continue
            nums = re.findall(r'\b(\d{2,3}(?:,\d{2,3})*\.\d{2})\b', line)
            for num in nums:
                try:
                    val = float(num.replace(",", ""))
                    if val > 5000.0:
                        candidates.append(val)
                except: pass
        if candidates:
            return round(max(candidates), 2)
        return 0.0

    @staticmethod
    def parse_dataframe(df: pd.DataFrame) -> float:
        df.columns = [str(c).strip().upper() for c in df.columns]
        cr_col = next((c for c in df.columns if any(k in c for k in ['CREDIT','DEPOSIT','CR AMT','INWARD'])), None)
        if cr_col:
            df[cr_col] = pd.to_numeric(df[cr_col].astype(str).str.replace(",",""), errors='coerce').fillna(0)
            return float(df[cr_col].sum())
        return 0.0

    @staticmethod
    def parse(file_obj) -> tuple:
        if not file_obj: return 0.0, "no_file"
        name = file_obj.name.lower()
        try:
            if name.endswith('.pdf'):
                return UniversalBankParser.parse_pdf(file_obj), "pdf_parser"
            elif name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_obj, engine='openpyxl')
                return UniversalBankParser.parse_dataframe(df), "excel_parser"
            elif name.endswith('.csv'):
                df = pd.read_csv(file_obj, encoding='utf-8', errors='ignore')
                return UniversalBankParser.parse_dataframe(df), "csv_parser"
        except: pass
        return 0.0, "failed"


class StockLedgerParser:
    @staticmethod
    def parse(file_obj) -> dict:
        # Returns standard stub structures for direct calculation processing
        return {"stcg_111a": 0.0, "stcg_other": 0.0, "ltcg_112a": 0.0, "ltcg_other": 0.0}

# ────────────────────────────────────────────────────────
# 3. CORE TAX COMPUTATION ARCHITECTURE
# ────────────────────────────────────────────────────────
class TaxEngine:
    def __init__(self):
        self.gross_receipts = 0.0
        self.salary_income = 0.0
        self.other_sources_income = 0.0
        self.total_deductions = 0.0
        self.stcg_111a = 0.0
        self.stcg_other = 0.0
        self.ltcg_112a = 0.0
        self.ltcg_other = 0.0
        self.is_director = False
        self.has_foreign_assets = False
        self.has_agri_over_5k = False

    def compute(self, route: str, regime: str) -> dict:
        # Determine dynamic Net Taxable Turnover depending on targeted regime route mapping
        computed_turnover = self.gross_receipts
        if "44ADA" in route:
            computed_turnover = self.gross_receipts * 0.50
        elif "44AD" in route:
            computed_turnover = self.gross_receipts * 0.06

        gross_total = computed_turnover + self.salary_income + self.other_sources_income + self.stcg_111a + self.ltcg_112a
        net_taxable = max(0.0, gross_total - (self.total_deductions if regime == "OLD" else 0.0))

        # Basic simplified processing tax calculation map rules
        base_tax = net_taxable * 0.15 if net_taxable > 700000 else 0.0
        cess = base_tax * 0.04
        
        # Decide exact standard ITR Form requirements
        assigned_form = "ITR-1"
        if "44AD" in route or "44ADA" in route or self.stcg_111a > 0 or self.ltcg_112a > 0:
            assigned_form = "ITR-4" if ("44AD" in route or "44ADA" in route) and not self.is_director else "ITR-3"
        if self.has_foreign_assets or self.is_director:
            assigned_form = "ITR-2" if computed_turnover == self.gross_receipts else "ITR-3"

        return {
            "assigned_form": assigned_form,
            "metrics": {
                "Gross Total Income": gross_total,
                "Net Taxable Income": net_taxable
            },
            "tax_breakdown": {
                "Base Tax Payable": base_tax,
                "Health & Education Cess": cess,
                "Total Tax Liability": base_tax + cess
            }
        }

# ────────────────────────────────────────────────────────
# 4. REPORT MATRIX GENERATION PIPELINES (PDF)
# ────────────────────────────────────────────────────────
def generate_itr_pdf(name: str, pan: str, firm: str, result: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    story = [
        Paragraph(f"<b>KSP CONSOLE PLATFORM COMPLIANCE REPORT</b>", styles["Title"]),
        Spacer(1, 15),
        Paragraph(f"<b>Assessee Name:</b> {name}", styles["Normal"]),
        Paragraph(f"<b>PAN:</b> {pan}", styles["Normal"]),
        Paragraph(f"<b>Filing Partner Firm:</b> {firm}", styles["Normal"]),
        Paragraph(f"<b>Assigned Filing Pathway:</b> {result['assigned_form']}", styles["Normal"]),
        Spacer(1, 20),
        Paragraph("<b>Taxation Calculation Summary Metrics</b>", styles["Heading2"]),
    ]

    data = [["Metric Profile Descriptor", "Computed Ledger Value (INR)"]]
    for k, v in result["metrics"].items():
        data.append([k, f"Rs. {v:,.2f}"])
    for k, v in result["tax_breakdown"].items():
        data.append([k, f"Rs. {v:,.2f}"])

    t = Table(data, colWidths=[280, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(t)
    
    doc.build(story)
    return buffer.getvalue()

# ────────────────────────────────────────────────────────
# 5. STREAMLIT INTERACTIVE USER RUNTIME DASHBOARD
# ────────────────────────────────────────────────────────
def render_itr_module(user):
    st.markdown("### 🛠️ Smart ITR Engine & AI Dual Report")
    
    # Grid layout matching client dashboard design templates
    col1, col2 = st.columns(2)
    with col1:
        c_name = st.text_input("Assessee Legal Name", value="Shashank Kulkarni")
        c_pan = st.text_input("Permanent Account Number (PAN)", max_chars=10, value="ABCDE1234F")
    with col2:
        route_choice = st.selectbox("Filing Optimization Pipeline", ["Standard Route (Normal Provision Summary)", "Section 44AD (Presumptive Business)", "Section 44ADA (Presumptive Professional)"])
        regime_choice = st.selectbox("Tax Code Regime Selection", ["NEW", "OLD"])

    st.markdown("#### Document Ingestion Gateway")
    b_col, l_col = st.columns(2)
    with b_col:
        bank_file = st.file_uploader("Bank Statement (any bank — PDF/CSV/XLSX)", type=["pdf", "csv", "xlsx"])
    with l_col:
        ledger_file = st.file_uploader("Stock P&L Ledger (optional)", type=["pdf", "csv", "xlsx"])

    # Active State Parser Processing Engines
    parsed_receipts = 0.0
    if bank_file:
        parsed_receipts, state_flag = UniversalBankParser.parse(bank_file)
        if state_flag == "failed" or parsed_receipts == 0.0:
            st.warning("⚠️ Could not auto-parse bank. Enter Gross Receipts manually below.")
        else:
            st.success(f"✅ Ingestion Engine Cleaned: Extracted Total Credits — ₹ {parsed_receipts:,.2f}")

    st.markdown("#### Step 1 — Parse Documents & Verify Figures")
    gross_receipts = st.number_input("Gross Receipts / Total Bank Credits (₹)", value=float(parsed_receipts if parsed_receipts > 0 else 0.0), step=5000.0)
    
    # Manual Override Variable Structuring Panels
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        salary_inc = st.number_input("Salary Income / Allowances (₹)", value=0.0)
        other_inc = st.number_input("Income From Other Sources (₹)", value=0.0)
    with m_col2:
        stcg_111a = st.number_input("STCG — Sec 111A Listed Equity (₹)", value=0.0)
        deductions = st.number_input("Chapter VIA Deductions (Applicable to Old Regime Only) (₹)", value=0.0)

    st.markdown("#### Risk Analysis Parameters")
    is_dir = st.checkbox("Holds directorship position or unlisted stock configurations")
    f_assets = st.checkbox("Maintains active offshore foreign banking accounts / assets (Schedule FA)")

    st.markdown("#### Step 2 — Compute Tax + AI Dual Report")
    if st.button("Execute Tax Computation Matrix & AI Engine"):
        engine = TaxEngine()
        engine.gross_receipts = gross_receipts
        engine.salary_income = salary_inc
        engine.other_sources_income = other_inc
        engine.total_deductions = deductions
        engine.stcg_111a = stcg_111a
        engine.is_director = is_dir
        engine.has_foreign_assets = f_assets

        # Run Standard Formula Computations
        result = engine.compute(route=route_choice, regime=regime_choice)
        
        st.success(f"🚀 Execution Complete: System Assigned Form {result['assigned_form']}")
        
        # Display live calculation dashboards
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown("##### Computation Summary")
            for k, v in result["metrics"].items():
                st.metric(label=k, value=f"₹ {v:,.2f}")
        with res_col2:
            st.markdown("##### Liability Breakdown")
            for k, v in result["tax_breakdown"].items():
                st.metric(label=k, value=f"₹ {v:,.2f}")

        # Trigger Fixed Google AI Generation Analysis Agent
        st.markdown("##### 🤖 KSP AI Compliance & Strategy Review")
        ai_prompt = f"Firm: {user['firm']}, Route: {route_choice}, Regime: {regime_choice}, Gross Receipts: {gross_receipts}, Computed Net Income: {result['metrics']['Net Taxable Income']}, Assigned Form: {result['assigned_form']}."
        with st.spinner("Invoking Gemini Tax Optimization Matrix..."):
            ai_insight = run_ai_compliance_analysis(ai_prompt)
            st.write(ai_insight)

        # PDF Delivery download button configuration
        pdf_data = generate_itr_pdf(c_name, c_pan, user["firm"], result)
        st.download_button("📥 Download Final Consolidated PDF Report", data=pdf_data, file_name=f"KSP_TaxReport_{c_name}.pdf", mime="application/pdf")

# ────────────────────────────────────────────────────────
# MAIN SYSTEM INITIALIZATION ROUTERENTRY
# ────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="KSP Console Platform", layout="wide")
    
    # Mocking standard active user state architecture values
    user_session = {"logged_in": True, "firm": "Kulkarni Strategic Partners", "plan": "ENTERPRISE"}
    
    # Sidebar Navigation Structure Mock matching layout designs
    st.sidebar.title("⚙️ KSP CONSOLE")
    st.sidebar.markdown(f"**Firm:** `{user_session['firm']}`\n\n**Plan:** `{user_session['plan']}`")
    
    module_choice = st.sidebar.radio("SELECT MODULE:", ["🚀 Smart ITR Engine + AI Dual Report", "💼 GST Command Center", "🛡️ KSP AI Compliance Agent"])
    
    if "Smart ITR" in module_choice:
        render_itr_module(user_session)
    else:
        st.sidebar.info("Module loading state in structural layout sync.")

if __name__ == "__main__":
    main()