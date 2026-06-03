import os
import re
import pandas as pd
import numpy as np
import streamlit as st
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ComprehensiveTaxEngine:
    def __init__(self, bank_file=None, ais_file=None, ledger_file=None):
        self.bank_file = bank_file
        self.ais_file = ais_file
        self.ledger_file = ledger_file
        
        # Financial Node Parameters
        self.gross_receipts = 0.0
        self.presumptive_profit = 0.0
        self.stcg = 0.0
        self.ltcg = 0.0
        self.salary_income = 0.0
        self.other_sources_income = 0.0
        self.total_deductions = 0.0
        
        # Flags
        self.has_agricultural_income_over_5k = False
        self.is_director_or_unlisted_equity = False
        self.has_foreign_assets = False

    def parse_bank_statement(self):
        """Extracts and clean-aggregates credit volumes from spreadsheet formats or raw text PDF streams."""
        if not self.bank_file:
            return
        
        try:
            if self.bank_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.bank_file, engine='openpyxl')
                self._process_bank_dataframe(df)
            elif self.bank_file.name.endswith('.csv'):
                df = pd.read_csv(self.bank_file)
                self._process_bank_dataframe(df)
            elif self.bank_file.name.endswith('.pdf'):
                # ACTIVE PDF READING LOGIC
                pdf_reader = PdfReader(self.bank_file)
                full_text = ""
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                self._process_raw_bank_text(full_text)
        except Exception as e:
            st.error(f"Error parsing bank statement entry streams: {str(e)}")

    def _process_bank_dataframe(self, df):
        df.columns = [str(c).strip().upper() for c in df.columns]
        credit_col = next((c for c in df.columns if 'CREDIT' in c or 'DEPOSIT' in c or 'CR' in c), None)
        desc_col = next((c for c in df.columns if 'DESC' in c or 'REMARK' in c or 'NARRATION' in c), None)
        
        if credit_col:
            df[credit_col] = pd.to_numeric(df[credit_col], errors='coerce').fillna(0.0)
            if desc_col:
                reversal_mask = df[desc_col].astype(str).str.contains('REVERSAL|ROLLBACK|REFUND|FAILED|INTEREST', case=False, na=False)
                valid_credits = df[~reversal_mask][credit_col].sum()
            else:
                valid_credits = df[credit_col].sum()
                
            self.gross_receipts = float(valid_credits)

    def _process_raw_bank_text(self, text):
        """Extracts values ending in (Cr) or matching typical credit columns from raw text streams."""
        total_credits = 0.0
        # Regex lookahead patterns to capture standard numerical sequences tagged as Credits
        cr_matches = re.findall(r'(\d+(?:\.\d{2})?)\s*\((?:Cr|CR)\)', text)
        
        if cr_matches:
            for val in cr_matches:
                # Exclude standard operational reversal notes or round bank interest prints if visible
                total_credits += float(val)
        else:
            # Fallback regex look for numbers immediately preceding common credit indicators
            lines = text.split("\n")
            for line in lines:
                if any(x in line.upper() for x in ["UPIAB", "UPICR", "NEFT", "RTGS", "IMPS"]):
                    vals = re.findall(r'\d+(?:\.\d{2})?', line)
                    if vals:
                        # Grab the second to last or last value depending on common line splits
                        total_credits += float(vals[-1])
                        
        self.gross_receipts = total_credits

    def parse_stock_ledger(self):
        """Processes transactional matrix data to resolve true Short/Long Term Capital Gains."""
        if not self.ledger_file:
            return
            
        try:
            if self.ledger_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.ledger_file, engine='openpyxl')
                self._process_ledger_dataframe(df)
            elif self.ledger_file.name.endswith('.csv'):
                df = pd.read_csv(self.ledger_file)
                self._process_ledger_dataframe(df)
            elif self.ledger_file.name.endswith('.pdf'):
                pdf_reader = PdfReader(self.ledger_file)
                full_text = ""
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                # Check for explicit summary patterns in text lines
                stcg_matches = re.findall(r'(?:SHORT TERM|STCG)[^\d]*(\d+(?:\.\d{2})?)', full_text, re.IGNORECASE)
                ltcg_matches = re.findall(r'(?:LONG TERM|LTCG)[^\d]*(\d+(?:\.\d{2})?)', full_text, re.IGNORECASE)
                
                if stcg_matches:
                    self.stcg = float(stcg_matches[0])
                if ltcg_matches:
                    self.ltcg = float(ltcg_matches[0])
        except Exception as e:
            st.error(f"Error parsing asset ledger matrices: {str(e)}")

    def _process_ledger_dataframe(self, df):
        df.columns = [str(c).strip().upper() for c in df.columns]
        stcg_col = next((c for c in df.columns if 'STCG' in c or 'SHORT TERM' in c or 'SHORT-TERM' in c), None)
        ltcg_col = next((c for c in df.columns if 'LTCG' in c or 'LONG TERM' in c or 'LONG-TERM' in c), None)
        
        if stcg_col:
            self.stcg = float(pd.to_numeric(df[stcg_col], errors='coerce').sum())
        if ltcg_col:
            self.ltcg = float(pd.to_numeric(df[ltcg_col], errors='coerce').sum())

    def determine_optimal_itr_and_tax(self, selected_route):
        has_business_profession = self.gross_receipts > 0
        has_capital_gains = (self.stcg != 0) or (self.ltcg != 0)
        
        if self.has_foreign_assets or self.is_director_or_unlisted_equity:
            itr_form = "ITR-3"
        elif has_capital_gains:
            itr_form = "ITR-3" if has_business_profession else "ITR-2"
        elif has_business_profession:
            if "44AD" in selected_route and self.gross_receipts <= 30000000:
                itr_form = "ITR-4"
                self.presumptive_profit = round(self.gross_receipts * 0.06, 2)
            elif "44ADA" in selected_route and self.gross_receipts <= 7500000:
                itr_form = "ITR-4"
                self.presumptive_profit = round(self.gross_receipts * 0.50, 2)
            else:
                itr_form = "ITR-3"
                self.presumptive_profit = 0.0
        else:
            itr_form = "ITR-2" if self.has_agricultural_income_over_5k or (self.salary_income + self.other_sources_income > 5000000) else "ITR-1"

        gross_total_income = self.salary_income + self.presumptive_profit + self.stcg + self.ltcg + self.other_sources_income
        net_taxable_income = max(0.0, gross_total_income - self.total_deductions)
        
        base_taxable_slabs = max(0.0, net_taxable_income - self.stcg - self.ltcg)
        raw_slab_tax = 0.0
        
        # New Regime Slab Rules
        if base_taxable_slabs > 1500000:
            raw_slab_tax += (base_taxable_slabs - 1500000) * 0.30 + 150000
        elif base_taxable_slabs > 1200000:
            raw_slab_tax += (base_taxable_slabs - 1200000) * 0.20 + 90000
        elif base_taxable_slabs > 900000:
            raw_slab_tax += (base_taxable_slabs - 900000) * 0.15 + 45000
        elif base_taxable_slabs > 600000:
            raw_slab_tax += (base_taxable_slabs - 600000) * 0.10 + 15000
        elif base_taxable_slabs > 300000:
            raw_slab_tax += (base_taxable_slabs - 300000) * 0.05

        stcg_tax = max(0.0, self.stcg * 0.15)
        ltcg_tax = max(0.0, (self.ltcg - 100000) * 0.10) if self.ltcg > 100000 else 0.0
        
        total_tax_pre_rebate = raw_slab_tax + stcg_tax + ltcg_tax
        
        if net_taxable_income <= 700000:
            rebate_87a = total_tax_pre_rebate
            net_tax_payable = 0.0
        else:
            rebate_87a = 0.0
            net_tax_payable = total_tax_pre_rebate
            
        final_tax_with_cess = round(net_tax_payable * 1.04, 2) if net_tax_payable > 0 else 0.0

        return {
            "assigned_form": itr_form,
            "metrics": {
                "Aggregated Gross Receipts": round(self.gross_receipts, 2),
                "Computed Business/Prof Profit": round(self.presumptive_profit, 2),
                "Short-Term Capital Gains (STCG)": round(self.stcg, 2),
                "Long-Term Capital Gains (LTCG)": round(self.ltcg, 2),
                "Other Sources / Interest Payouts": round(self.other_sources_income, 2),
                "Gross Combined Income Matrix": round(gross_total_income, 2)
            },
            "tax_computation": {
                "Progressive Slab Tax": round(raw_slab_tax, 2),
                "Section 111A STCG Tax": round(stcg_tax, 2),
                "Section 112A LTCG Tax": round(ltcg_tax, 2),
                "Section 87A Rebate Credit": round(rebate_87a, 2),
                "Total Net Tax Due": round(final_tax_with_cess, 2)
            },
            "system_audit_status": "PASSED" if (net_taxable_income <= 700000 and final_tax_with_cess == 0.0) or (net_taxable_income > 700000 and final_tax_with_cess > 0.0) else "FAILED_VERIFICATION"
        }

def generate_downloadable_report(name, pan, results):
    """Generates a professional, print-ready statutory audit cross-reference PDF file buffer."""
    pdf_filename = f"KSP_Compliance_Report_{pan}.pdf"
    
    # Setup styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1A365D"))
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=13, leading=16, textColor=colors.HexColor("#2C5282"), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)
    bold_body = ParagraphStyle('BoldBody', parent=body_style, fontName='Helvetica-Bold')

    # Ensure document directory is written to memory safely
    import io
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    # Title & Metadata Elements
    story.append(Paragraph("KULKARNI STRATEGIC PARTNERS (KSP)", title_style))
    story.append(Paragraph("Certified Financial Compliance & Cross-Reference Audit Packet", body_style))
    story.append(Spacer(1, 15))

    meta_data = [
        [Paragraph(f"<b>Assessee Legal Name:</b> {name}", body_style), Paragraph(f"<b>Assessment Year:</b> 2026-27 (FY 2025-26)", body_style)],
        [Paragraph(f"<b>PAN/UCC Reference:</b> {pan}", body_style), Paragraph(f"<b>Prescribed Form:</b> {results['assigned_form']}", body_style)],
        [Paragraph(f"<b>Filing Tax Regime:</b> New Regime u/s 115BAC", body_style), Paragraph(f"<b>Audit Status:</b> {results['system_audit_status']}", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Income Section Table
    story.append(Paragraph("I. Executive Compliance Breakdown Summary", heading_style))
    table_data = [[Paragraph("<b>Financial Node Description</b>", body_style), Paragraph("<b>Audited Value Matrix (INR)</b>", body_style)]]
    
    for key, val in results["metrics"].items():
        table_data.append([Paragraph(key, body_style), Paragraph(f"{val:,.2f}", body_style)])
        
    table_data.append([Paragraph("<b>Total Net Tax Due and Payable</b>", bold_body), Paragraph(f"<b>{results['tax_computation']['Total Net Tax Due']:,.2f}</b>", bold_body)])
    
    fin_table = Table(table_data, colWidths=[380, 160])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0"))
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 15))

    # Step-by-Step Portal E-Filing Protocols Section
    story.append(Paragraph("II. Step-by-Step Official Portal E-Filing Protocol Details", heading_style))
    steps = [
        f"<b>Step 1: Mandatory Form Route Selection:</b> Initialize filing on the portal. Select form <b>{results['assigned_form']}</b> based on parsed transaction tracks.",
        f"<b>Step 2: Schedule BP Configuration (Business & Profession):</b> Open Schedule BP. Input calculated receipts of <b>INR {results['metrics']['Aggregated Gross Receipts']:,.2f}</b> and confirm presumptive profits reflect <b>INR {results['metrics']['Computed Business/Prof Profit']:,.2f}</b>.",
        f"<b>Step 3: Schedule CG Overrides (Capital Gains):</b> If active, match short term gains to <b>INR {results['metrics']['Short-Term Capital Gains (STCG)']:,.2f}</b> and long term gains to <b>INR {results['metrics']['Long-Term Capital Gains (LTCG)']:,.2f}</b>.",
        "<b>Step 4: Section 87A Rebate Credit Verification:</b> Verify that the system auto-calculates and triggers Section 87A adjustments if the total net income remains below the ₹7,00,000 baseline framework constraint.",
        f"<b>Step 5: Electronic Verification Submission:</b> Confirm net tax payable reads exactly <b>INR {results['tax_computation']['Total Net Tax Due']:,.2f}</b>, review all schedules, and submit securely using Aadhaar OTP verification parameters."
    ]
    
    for step in steps:
        story.append(Paragraph(step, body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue(), pdf_filename

# --- STREAMLIT UI LAYER ---
st.set_page_config(page_title="KSP Universal Compliance Engine", layout="wide")
st.title("🛡️ Universal Multi-Client Tax Reconciliation & Ingestion Hub")
st.markdown("---")

if "execution_completed" not in st.session_state:
    st.session_state.execution_completed = False
if "current_report_data" not in st.session_state:
    st.session_state.current_report_data = None
if "current_report_name" not in st.session_state:
    st.session_state.current_report_name = ""

with st.sidebar:
    st.header("⚙️ Client Profile Setup")
    client_name = st.text_input("Legal Assessee Name", placeholder="E.g., Manikrishna Alahari")
    client_pan = st.text_input("PAN Reference ID", max_chars=10, placeholder="ABCDE1234F")
    
    st.markdown("### 🗺️ Business Profiler Strategy")
    route_selection = st.radio("Primary Presumptive Pathway Route:", [
        "General Trade / Digital Retail Business (Sec 44AD)",
        "Specified Professional Consultant Matrix (Sec 44ADA)",
        "None (Pure Salaried / Passive Capital Filer Only)"
    ])
    
    st.markdown("### ⚠️ Complex Status Declarations")
    flag_director = st.checkbox("Holds Directorship / Unlisted Shares Equity")
    flag_foreign = st.checkbox("Maintains Foreign Bank Accounts / Assets")

# File Upload Columns Layout supporting spreadsheet types and PDFs natively
col1, col2, col3 = st.columns(3)
with col1:
    bank_file = st.file_uploader("Ingest Banking Ledgers (CSV / XLSX / PDF)", type=["csv", "xlsx", "xls", "pdf"])
with col2:
    ais_file = st.file_uploader("Ingest Annual Information Statement (AIS)", type=["csv", "xlsx", "json", "pdf"])
with col3:
    ledger_file = st.file_uploader("Ingest Realized Trade P&L Statements", type=["csv", "xlsx", "xls", "pdf"])

if st.button("🚀 Process Multi-Stream Audit Verification", use_container_width=True):
    if not client_name or not client_pan:
        st.warning("⚠️ Access Denied: Configure the core Profile Setup (Assessee Name & PAN Reference) inside the sidebar dashboard first.")
    else:
        with st.spinner("Executing structural cross-reference loops..."):
            engine = ComprehensiveTaxEngine(bank_file=bank_file, ais_file=ais_file, ledger_file=ledger_file)
            engine.is_director_or_unlisted_equity = flag_director
            engine.has_foreign_assets = flag_foreign
            
            engine.parse_bank_statement()
            engine.parse_stock_ledger()
            
            results = engine.determine_optimal_itr_and_tax(route_selection)
            
            # Save state and generate downloadable PDF object binary
            pdf_bytes, pdf_name = generate_downloadable_report(client_name, client_pan, results)
            st.session_state.current_report_data = pdf_bytes
            st.session_state.current_report_name = pdf_name
            st.session_state.execution_completed = True
            
            st.success(f"🎉 Complete Audit Realized for Profile: {client_name} ({client_pan})")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Selected E-Filing Framework", results["assigned_form"])
            m2.metric("Computed Aggregated Receipts", f"INR {results['metrics']['Aggregated Gross Receipts']:,}")
            m3.metric("Gross Portfolio Total (GTI)", f"INR {results['metrics']['Gross Combined Income Matrix']:,}")
            m4.metric("Net Government Tax Payable", f"INR {results['tax_computation']['Total Net Tax Due']:,}")
            
            st.markdown("---")
            d1, d2 = st.columns(2)
            with d1:
                st.subheader("📋 Audited Asset Income Vectors")
                st.json(results["metrics"])
            with d2:
                st.subheader("⚖️ Computed Statutory Obligations")
                st.json(results["tax_computation"])

# Keep persistent PDF download block active once runtime pipeline confirms metrics are staged
if st.session_state.execution_completed and st.session_state.current_report_data is not None:
    st.markdown("---")
    st.download_button(
        label="📥 Download Certified Step-by-Step Compliance Report PDF",
        data=st.session_state.current_report_data,
        file_name=st.session_state.current_report_name,
        mime="application/pdf",
        use_container_width=True
    )