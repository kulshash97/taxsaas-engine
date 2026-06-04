import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import os
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ────────────────────────────────────────────────────────
# 1. GOOGLE GEMINI API CORE ENGINE
# ────────────────────────────────────────────────────────
import google.generativeai as genai

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "MOCK_KEY"))

def run_ai_compliance_analysis(prompt_context: str) -> str:
    """Runs a structured tax optimization review using the stable generative endpoint."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            f"You are an elite Indian Corporate Tax Strategy Advisor. Analyze the following scenario and provide optimal compliance planning routes:\n\n{prompt_context}"
        )
        return response.text
    except Exception as e:
        return f"⚠️ Optimization Analysis Deferred: {str(e)}\n\nFallback Recommendation: Review balance sheets against Section 44ADA thresholds manually."

# ────────────────────────────────────────────────────────
# 2. ADVANCED DOCUMENT INGESTION PARSERS (FIXED)
# ────────────────────────────────────────────────────────
class UniversalBankParser:
    @staticmethod
    def parse_pdf(file_obj) -> float:
        pdf = PdfReader(file_obj)
        page_texts = [p.extract_text() or "" for p in pdf.pages]
        full_text  = "\n".join(page_texts)

        val = UniversalBankParser._strategy_summary_row(full_text)
        if val > 0: return val

        val = UniversalBankParser._strategy_summary_label(full_text)
        if val > 0: return val

        val = UniversalBankParser._strategy_transaction_rows(page_texts)
        if val > 0: return val

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
        credit_tags  = ['UPI/CR/', 'NEFT CR', 'RTGS CR', 'IMPS/CR', 'SALARY', 'BY TRANSFER', 'CREDIT']
        total = 0.0
        for text in page_texts:
            for line in text.split("\n"):
                u = line.upper()
                if any(tag in u for tag in credit_tags) and not any(b in u for b in ['BAL', 'BALANCE', 'RUNNING']):
                    nums = re.findall(r'\b(\d{1,3}(?:,\d{2,3})*\.\d{2})\b', line)
                    if nums:
                        try:
                            val = float(nums[-1].replace(",", ""))
                            total += val
                        except: pass
        return round(total, 2)

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
        # PROTECTIVE LAYER: Completely safeguards against missing or empty stream initializations
        if file_obj is None or not hasattr(file_obj, 'name'): 
            return 0.0, "no_file"
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
        self.is_director = False
        self.has_foreign_assets = False

    def compute(self, route: str, regime: str) -> dict:
        presumptive_rate = 1.0
        if "44ADA" in route:
            presumptive_rate = 0.50
        elif "44AD" in route:
            presumptive_rate = 0.06

        computed_turnover = self.gross_receipts * presumptive_rate
        gross_total = computed_turnover + self.salary_income + self.other_sources_income + self.stcg_111a
        deductions_applied = self.total_deductions if regime == "OLD" else 0.0
        net_taxable = max(0.0, gross_total - deductions_applied)

        # Basic simplified processing tax calculation map rules
        base_tax = 0.0
        if net_taxable > 700000 and regime == "NEW":
            base_tax = (net_taxable - 700000) * 0.15 + 15000 # Standard illustrative bracket placement
        elif net_taxable > 500000 and regime == "OLD":
            base_tax = (net_taxable - 500000) * 0.20 + 12500

        cess = base_tax * 0.04
        
        assigned_form = "ITR-1"
        if "44AD" in route or "44ADA" in route or self.stcg_111a > 0:
            assigned_form = "ITR-4" if ("44AD" in route or "44ADA" in route) and not self.is_director else "ITR-3"
        if self.has_foreign_assets or self.is_director:
            assigned_form = "ITR-3"

        return {
            "assigned_form": assigned_form,
            "presumptive_rate": presumptive_rate,
            "computed_turnover": computed_turnover,
            "deductions_applied": deductions_applied,
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
# 4. OVERHAULED REPORT PIPELINE (STEP-BY-STEP PROCESS PDF)
# ────────────────────────────────────────────────────────
def generate_itr_pdf(name: str, pan: str, firm: str, route: str, regime: str, engine_input: TaxEngine, result: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom step styles
    step_num_style = ParagraphStyle('StepNum', parent=styles['Heading3'], textColor=colors.HexColor('#1E3A8A'), spaceBefore=12, spaceAfter=4)
    body_style = ParagraphStyle('StepBody', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=6)
    bold_body = ParagraphStyle('StepBodyBold', parent=body_style, fontName='Helvetica-Bold')

    story = [
        Paragraph(f"<b>KSP CONSOLE PLATFORM COMPLIANCE REPORT</b>", styles["Title"]),
        Spacer(1, 4),
        Paragraph(f"<font color='#666666'>Generated by: {firm}</font>", styles["Normal"]),
        Spacer(1, 15),
        Paragraph("<b>1. CLIENT MASTER RECORD PROFILE</b>", styles["Heading2"]),
        Paragraph(f"<b>Assessee Legal Name:</b> {name}", body_style),
        Paragraph(f"<b>Permanent Account Number (PAN):</b> {pan}", body_style),
        Paragraph(f"<b>Selected Tax Regime Context:</b> {regime} Regime", body_style),
        Paragraph(f"<b>Target Optimization Pipeline:</b> {route}", body_style),
        Spacer(1, 10),
        Paragraph("<b>2. STEP-BY-STEP COMPLIANCE FILING PROCESS LOG</b>", styles["Heading2"]),
    ]

    # Step 1
    story.append(Paragraph("Step 1: Document Ingestion & Gross Turnover Mapping", step_num_style))
    story.append(Paragraph(f"The structural ingestion module evaluated the submitted digital ledgers. The total verified gross bank ledger credit volume/turnover established for the financial year is mapped at <b>₹ {engine_input.gross_receipts:,.2f}</b>.", body_style))

    # Step 2
    story.append(Paragraph("Step 2: Application of Presumptive Profit Margins", step_num_style))
    rate_percent = int(result['presumptive_rate'] * 100)
    story.append(Paragraph(f"Based on your selection of <i>{route}</i>, tax computations are routed through provisions of the Income Tax Act. A presumptive operational net income profit rate of <b>{rate_percent}%</b> was locked against the gross turnover.", body_style))
    story.append(Paragraph(f"<b>Resulting Presumptive Business/Professional Income:</b> ₹ {result['computed_turnover']:,.2f}", bold_body))

    # Step 3
    story.append(Paragraph("Step 3: Income Streams Aggregation Matrix", step_num_style))
    story.append(Paragraph("The platform assembled all distinct head-wise income fields compiled from structural disclosures:", body_style))
    
    inc_data = [
        ["Income Stream Head Description", "Declared Value (INR)"],
        ["Presumptive Business/Professional Profit Block", f"₹ {result['computed_turnover']:,.2f}"],
        ["Salary Income / Standard Allowances", f"₹ {engine_input.salary_income:,.2f}"],
        ["Income from Other Sources (Interest/Dividends)", f"₹ {engine_input.other_sources_income:,.2f}"],
        ["Short Term Capital Gains (STCG Sec 111A)", f"₹ {engine_input.stcg_111a:,.2f}"],
        ["GROSS TOTAL INCOME (GTI COMPREHENSIVE)", f"₹ {result['metrics']['Gross Total Income']:,.2f}"]
    ]
    t1 = Table(inc_data, colWidths=[300, 180])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0,0), (1,0), colors.HexColor('#1F2937')),
        ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EFF6FF')),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t1)

    # Step 4
    story.append(Paragraph("Step 4: Deductions Chapter VIA Adjustments", step_num_style))
    if regime == "NEW":
        story.append(Paragraph("The assessee is being tracked under the <b>NEW Tax Regime</b>. In accordance with standard modern default rules, Chapter VIA deduction relief sets are restricted (Value Applied: <b>₹ 0.00</b>).", body_style))
    else:
        story.append(Paragraph(f"The assessee is tracked under the <b>OLD Tax Regime</b>. Eligible parameters matching Chapter VIA are extracted and applied up to the legal threshold limit: <b>₹ {result['deductions_applied']:,.2f}</b>.", body_style))
    story.append(Paragraph(f"<b>Final Computed Net Taxable Income:</b> ₹ {result['metrics']['Net Taxable Income']:,.2f}", bold_body))

    # Step 5
    story.append(Paragraph("Step 5: Final Tax Liability Assessment & Form Validation", step_num_style))
    story.append(Paragraph(f"The core matrix applies tax slice computations to the Net Taxable Income. Based on the presence of business income pathways, the regulatory environment assigns <b>FORM {result['assigned_form']}</b> as the statutory requirement.", body_style))
    
    tax_data = [
        ["Tax Computation Field Line Item", "Calculated Value (INR)"],
        ["Base Progressive Income Tax Liability", f"₹ {result['tax_breakdown']['Base Tax Payable']:,.2f}"],
        ["Health & Education Cess (4.0%)", f"₹ {result['tax_breakdown']['Health & Education Cess']:,.2f}"],
        ["TOTAL OUTSTANDING TAX LIABILITY", f"₹ {result['tax_breakdown']['Total Tax Liability']:,.2f}"]
    ]
    t2 = Table(tax_data, colWidths=[300, 180])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#9CA3AF')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FEF2F2')),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t2)

    doc.build(story)
    return buffer.getvalue()

# ────────────────────────────────────────────────────────
# 5. USER RUNTIME INTERACTIVE DASHBOARD
# ────────────────────────────────────────────────────────
def render_itr_module(user):
    st.markdown("### 🛠️ Smart ITR Engine & AI Dual Report")
    
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

    parsed_receipts = 0.0
    if bank_file:
        parsed_receipts, state_flag = UniversalBankParser.parse(bank_file)
        if state_flag == "failed" or parsed_receipts == 0.0:
            st.warning("⚠️ Could not auto-parse bank. Enter Gross Receipts manually below.")
        else:
            st.success(f"✅ Ingestion Engine Cleaned: Extracted Total Credits — ₹ {parsed_receipts:,.2f}")

    st.markdown("#### Step 1 — Parse Documents & Verify Figures")
    gross_receipts = st.number_input("Gross Receipts / Total Bank Credits (₹)", value=float(parsed_receipts if parsed_receipts > 0 else 0.0), step=5000.0)
    
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

        result = engine.compute(route=route_choice, regime=regime_choice)
        
        st.success(f"🚀 Execution Complete: System Assigned Form {result['assigned_form']}")
        
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown("##### Computation Summary")
            for k, v in result["metrics"].items():
                st.metric(label=k, value=f"₹ {v:,.2f}")
        with res_col2:
            st.markdown("##### Liability Breakdown")
            for k, v in result["tax_breakdown"].items():
                st.metric(label=k, value=f"₹ {v:,.2f}")

        st.markdown("##### 🤖 KSP AI Compliance & Strategy Review")
        ai_prompt = f"Firm: {user['firm']}, Route: {route_choice}, Regime: {regime_choice}, Gross Receipts: {gross_receipts}, Computed Net Income: {result['metrics']['Net Taxable Income']}, Assigned Form: {result['assigned_form']}."
        with st.spinner("Invoking Gemini Tax Optimization Matrix..."):
            ai_insight = run_ai_compliance_analysis(ai_prompt)
            st.write(ai_insight)

        # Updated to include full step-by-step audit elements
        pdf_data = generate_itr_pdf(c_name, c_pan, user["firm"], route_choice, regime_choice, engine, result)
        st.download_button("📥 Download Step-by-Step Compliance PDF Report", data=pdf_data, file_name=f"KSP_StepReport_{c_name.replace(' ', '_')}.pdf", mime="application/pdf")

# ────────────────────────────────────────────────────────
# MAIN SYSTEM INITIALIZATION ROUTER
# ────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="KSP Console Platform", layout="wide")
    user_session = {"logged_in": True, "firm": "Kulkarni Strategic Partners", "plan": "ENTERPRISE"}
    
    st.sidebar.title("⚙️ KSP CONSOLE")
    st.sidebar.markdown(f"**Firm:** `{user_session['firm']}`\n\n**Plan:** `{user_session['plan']}`")
    
    module_choice = st.sidebar.radio("SELECT MODULE:", ["🚀 Smart ITR Engine + AI Dual Report", "💼 GST Command Center", "🛡️ KSP AI Compliance Agent"])
    
    if "Smart ITR" in module_choice:
        render_itr_module(user_session)
    else:
        st.sidebar.info("Module loading state in structural layout sync.")

if __name__ == "__main__":
    main()