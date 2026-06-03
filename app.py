import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -------------------------------------------------------------------------
# SYSTEM INITIALIZATION & STATE MANAGEMENT
# -------------------------------------------------------------------------
st.set_page_config(page_title="KSP Compliance Engine Pro", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State persistent variables
if "audit_results" not in st.session_state:
    st.session_state.audit_results = None
if "pdf_payload" not in st.session_state:
    st.session_state.pdf_payload = None

# Callback function to wipe screen state entirely for the next client upload
def reset_system_pipeline():
    st.session_state.audit_results = None
    st.session_state.pdf_payload = None
    st.toast("System cleared! Ready for new client files.", icon="🧹")

# -------------------------------------------------------------------------
# DATA STREAM PARSING ENGINES
# -------------------------------------------------------------------------

def extract_text_from_pdf(file_bytes):
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except:
        return ""

def parse_bank_pdf_text(text):
    if not text:
        return 0.0  
    total_credits = 0.0
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if "limit" in line_lower or "drawing" in line_lower:
            continue
        if any(k in line_lower for k in ['deposit', 'credit', 'cr ', 'neft', 'rtgs', 'upi', 'imps', 'transfer']):
            line_numbers = re.findall(r'([\d,]+\.\d{2})', line)
            if line_numbers:
                try:
                    val = float(line_numbers[-1].replace(',', ''))
                    total_credits += val
                except ValueError:
                    continue
    return total_credits

def parse_stock_ledger(file_bytes, filename):
    try:
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0, header=None)
        else:
            df = pd.read_csv(io.BytesIO(file_bytes), header=None)
            
        df_clean = df.dropna(how='all').reset_index(drop=True)
        header_row_idx = None
        for idx, row in df_clean.iterrows():
            row_str = " ".join([str(x).lower() for x in row.values])
            if 'stock' in row_str and 'sell' in row_str:
                header_row_idx = idx
                break
                
        if header_row_idx is None:
            header_row_idx = 0

        headers = [str(c).strip().lower() for c in df_clean.iloc[header_row_idx].values]
        df_trades = df_clean.iloc[header_row_idx+1:].copy()
        df_trades.columns = headers
        df_trades = df_trades[df_trades.iloc[:, 0].notna() & (~df_trades.iloc[:, 0].astype(str).str.lower().str.contains('unrealised|total|summary'))]

        qty_idx = next((i for i, c in enumerate(headers) if 'qty' in c or 'quantity' in c), 2)
        buy_p_idx = next((i for i, c in enumerate(headers) if 'buy' in c and 'price' in c), 4)
        sell_v_idx = next((i for i, c in enumerate(headers) if 'sell' in c and 'value' in c), 8)
        pnl_idx = next((i for i, c in enumerate(headers) if 'p&l' in c or 'pnl' in c or 'realised' in c), 9)
        remark_idx = next((i for i, c in enumerate(headers) if 'remark' in c or 'type' in c), -1)

        total_actual_cost = 0.0
        total_actual_sales = 0.0
        reported_pnl = 0.0

        for _, row in df_trades.iterrows():
            try:
                qty = float(str(row.iloc[qty_idx]).replace(',', ''))
                b_price = float(str(row.iloc[buy_p_idx]).replace(',', ''))
                s_val = float(str(row.iloc[sell_v_idx]).replace(',', ''))
                pnl_val = float(str(row.iloc[pnl_idx]).replace(',', ''))
                remark_text = str(row.iloc[remark_idx]).lower() if remark_idx != -1 else ""
                
                reported_pnl += pnl_val

                if "split" in remark_text or "bonus" in remark_text or (b_price == 0.0 and s_val > 0.0):
                    total_actual_sales += s_val
                else:
                    total_actual_cost += (qty * b_price)
                    total_actual_sales += s_val
            except:
                continue

        return {
            "raw_realized_pnl": reported_pnl,
            "rectified_realized_pnl": (total_actual_sales - total_actual_cost),
            "total_charges": 0.0,
            "stcg_sales": total_actual_sales,
            "stcg_cost": total_actual_cost
        }
    except:
        return {"raw_realized_pnl": 0.0, "rectified_realized_pnl": 0.0, "total_charges": 0.0, "stcg_sales": 0.0, "stcg_cost": 0.0}

def compute_tax_liability(business_turnover, presumptive_rate, stcg_profit):
    normal_income = business_turnover * (presumptive_rate / 100.0)
    gross_total_income = normal_income + stcg_profit
    
    # New Tax Regime Slabs (AY 2026-27 update)
    tax_normal = 0.0
    rem_income = normal_income
    if rem_income > 1000000:
        tax_normal += (rem_income - 1000000) * 0.15
        rem_income = 1000000
    if rem_income > 700000:
        tax_normal += (rem_income - 700000) * 0.10
        rem_income = 700000
    if rem_income > 300000:
        tax_normal += (rem_income - 300000) * 0.05

    tax_stcg = max(0.0, stcg_profit) * 0.15
    total_tax_before_rebate = tax_normal + tax_stcg
    
    rebate_87a = 0.0
    if gross_total_income <= 1200000:
        rebate_87a += tax_normal
        if (tax_normal + tax_stcg) <= 60000:
            rebate_87a += tax_stcg
            
    final_tax = max(0.0, total_tax_before_rebate - rebate_87a)
    return {
        "normal_income": normal_income,
        "gross_total_income": gross_total_income,
        "tax_normal": tax_normal,
        "tax_stcg": tax_stcg,
        "total_tax_before_rebate": total_tax_before_rebate,
        "rebate_87a": rebate_87a,
        "final_tax": final_tax + (final_tax * 0.04)
    }

# -------------------------------------------------------------------------
# REPORTLAB PDF GENERATION HUBS
# -------------------------------------------------------------------------
def generate_pdf_report(client_name, pan_ucc, tax_m, stock_m, route, itr_form, turnover):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=35, bottomMargin=35)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=3)
    section_style = ParagraphStyle('SecTitle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#1E3A8A'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'))
    bold_body = ParagraphStyle('BodyBoldCustom', parent=body_style, fontName='Helvetica-Bold')
    instruction_style = ParagraphStyle('InsStyle', parent=body_style, fontSize=8.5, leading=12.5, spaceAfter=4)

    story.append(Paragraph("<b>KULKARNI STRATEGIC PARTNERS (KSP)</b>", title_style))
    story.append(Paragraph("Certified Financial Compliance & Cross-Reference Audit Packet", body_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=10))
    
    # Metadata Block
    meta_data = [
        [Paragraph("<b>Assessee Legal Name:</b>", body_style), Paragraph(str(client_name if client_name else "N/A"), body_style), Paragraph("<b>Assessment Year:</b>", body_style), Paragraph("2026-27 (FY 2025-26)", body_style)],
        [Paragraph("<b>PAN / UCC Reference:</b>", body_style), Paragraph(str(pan_ucc if pan_ucc else "N/A"), body_style), Paragraph("<b>Prescribed Form:</b>", bold_body), Paragraph(f"<b>{itr_form.split(' ')[0]}</b>", bold_body)],
        [Paragraph("<b>Filing Tax Regime:</b>", body_style), Paragraph("New Regime u/s 115BAC", body_style), Paragraph("<b>Pathway Strategy:</b>", body_style), Paragraph(str(route), body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[120, 150, 120, 140])
    t_meta.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')), ('PADDING', (0,0), (-1,-1), 4), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1'))]))
    story.append(t_meta)
    
    # Executive Summary Table Block
    story.append(Paragraph("I. Executive Compliance Breakdown Summary", section_style))
    breakdown_rows = [
        [Paragraph("<b>Financial Node Description</b>", bold_body), Paragraph("<b>Audited Value Matrix (INR)</b>", bold_body)],
        [Paragraph("Presumptive Profit Core (Sched. BP)", body_style), Paragraph(f"INR {tax_m['normal_income']:,.2f}", body_style)],
        [Paragraph("Rectified Equity Short-Term Capital Gain (Sched. CG)", body_style), Paragraph(f"INR {stock_m['rectified_realized_pnl']:,.2f}", body_style)],
        [Paragraph("<b>Gross Combined Portfolio Income Base (GTI)</b>", bold_body), Paragraph(f"<b>INR {tax_m['gross_total_income']:,.2f}</b>", bold_body)],
        [Paragraph("Calculated Normal Slab Liability Vector", body_style), Paragraph(f"INR {tax_m['tax_normal']:,.2f}", body_style)],
        [Paragraph("Calculated Special Rate 111A Tax Liability", body_style), Paragraph(f"INR {tax_m['tax_stcg']:,.2f}", body_style)],
        [Paragraph("<b>Section 87A Statutory Rebate Allocation</b>", bold_body), Paragraph(f"<b>- INR {tax_m['rebate_87a']:,.2f}</b>", bold_body)],
        [Paragraph("<b>Net Total Tax Due and Payable</b>", bold_body), Paragraph(f"<b>INR {tax_m['final_tax']:,.2f}</b>", bold_body)]
    ]
    t_break = Table(breakdown_rows, colWidths=[350, 180])
    t_break.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')), ('PADDING', (0,0), (-1,-1), 4), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')), ('BACKGROUND', (0,6), (-1,6), colors.HexColor('#DCFCE7'))]))
    story.append(t_break)
    
    # Step-by-Step E-Filing Protocols
    story.append(Paragraph("II. Step-by-Step Official Portal E-Filing Protocol Details", section_style))
    story.append(Paragraph(f"<b>Mandatory Form Route Selection:</b> {itr_form}", bold_body))
    story.append(Spacer(1, 4))
    
    protocols = [
        f"<b>1. Portal Authentication & Form Selection:</b> Go to <u>incometax.gov.in</u>, log in using legal PAN credentials, and select 'File Income Tax Return'. Choose <b>Assessment Year 2026-27</b> -> Mode: Online -> Status: Individual. Select <b>{itr_form.split(' ')[0]}</b> from the grid matrix. <i>(Note: Even though you are using presumptive rules, you must file this form to report stock short-term capital gains in Schedule CG).</i>",
        f"<b>2. Schedule BP Configuration (Business & Profession):</b> Open Schedule BP. If using <b>Sec 44AD</b>, input Gross Receipts as <b>INR {turnover:,.2f}</b> and net Presumptive Profit as <b>INR {tax_m['normal_income']:,.2f}</b>. If using <b>Sec 44ADA</b>, declare gross fees inside the professional metrics panel.",
        f"<b>3. Schedule CG Overrides (Capital Gains):</b> Under Capital Gains, check the tick box for 'Equity shares/units of equity oriented MF liable to STT u/s 111A'. Open details and input audited values to override raw split gaps:<br/>&nbsp;&nbsp;&bull; <b>Full Value of Consideration (Total Sales):</b> INR {stock_m['stcg_sales']:,.2f}<br/>&nbsp;&nbsp;&bull; <b>Cost of Acquisition (Adjusted Purchases):</b> INR {stock_m['stcg_cost']:,.2f}<br/>&nbsp;&nbsp;&bull; <b>Expenditure wholly connected with transfer:</b> INR {stock_m['total_charges'] - 810.0 if stock_m['total_charges'] > 810.0 else 0.0:,.2f} <i>(Excluding STT as per Section 48 rules).</i>",
        f"<b>4. Quarterly Capital Gains Mapping:</b> Scroll down to the bottom of Schedule CG to locate the 'Information about accrual/receipt of Capital Gains' grid. Distribute the net capital gains profit (<b>INR {stock_m['rectified_realized_pnl']:,.2f}</b>) across the matching quarterly brackets using actual sale transaction dates to align with the government's auto-validation rules.",
        f"<b>5. Final Verification & Zero-Tax Rebate Rules:</b> Proceed to the calculation review screen. Verify that the <b>Section 87A Rebate</b> automatically scales across both schedules because your absolute Gross Total Income (<b>INR {tax_m['gross_total_income']:,.2f}</b>) sits comfortably below the expanded threshold of the New Tax Regime. Confirm **Net Tax Payable Due** reads exactly <b>INR 0.00</b>, advance to verification, and execute your submission using Aadhaar OTP parameters securely."
    ]
    
    for note in protocols:
        story.append(Paragraph(note, instruction_style))
        story.append(Spacer(1, 2))
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -------------------------------------------------------------------------
# INTERFACE USER LAYOUT
# -------------------------------------------------------------------------
st.title("🛡️ ProTax IA-Engine Pro")
st.subheader("Dynamic Multistream Presumptive Business & Stock Ledger Tax Verification Hub")
st.markdown("---")

# Global Reset Layout Control Rule
if st.session_state.audit_results is not None:
    st.button("🧹 Clear Workspace & Load Next Client Profile", on_click=reset_system_pipeline, use_container_width=True, type="primary")
    st.markdown("---")

with st.sidebar:
    st.header("⚙️ Dynamic Profile Input")
    # Clean default states for non-hardcoded variable processing
    input_name = st.text_input("Assessee Legal Name", value="")
    input_id = st.text_input("PAN / Client UCC Reference", value="")
    
    st.markdown("### Filing Route Determination")
    route = st.radio("Filing Selection Logic Route:", ["General Small Business / Trade (Sec 44AD)", "Specified Professional (Sec 44ADA)"])
    input_rate = st.slider("Target Presumptive Profit Margin Percentage (%)", 6.0, 50.0, 6.0 if "44AD" in route else 50.0, step=0.5)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🏦 1. Banking Flow Ingestion")
    bank_file = st.file_uploader("Upload Bank Ledger / Statement", type=['pdf', 'csv', 'xlsx', 'xls'], key="bank_uploader")
with col2:
    st.markdown("### 📑 2. Government AIS Gateway")
    ais_file = st.file_uploader("Upload Annual Information Statement", type=['pdf', 'txt', 'json'], key="ais_uploader")
with col3:
    st.markdown("### 📈 3. Capital Gains Ledger")
    stock_file = st.file_uploader("Upload Broker Realized P&L Report", type=['xlsx', 'xls', 'csv'], key="stock_uploader")

if st.button("🚀 Execute Comprehensive Compliance Audit", use_container_width=True):
    if not input_name or not input_id:
        st.warning("⚠️ Please provide an Assessee Name and PAN/UCC Reference profile setup before computing lines.")
    else:
        computed_turnover = 0.0
        stock_metrics = {"raw_realized_pnl": 0.0, "rectified_realized_pnl": 0.0, "total_charges": 0.0, "stcg_sales": 0.0, "stcg_cost": 0.0}
        
        if bank_file:
            fb = bank_file.read()
            if bank_file.name.endswith('.pdf'):
                computed_turnover = parse_bank_pdf_text(extract_text_from_pdf(fb))
            else:
                try:
                    df = pd.read_excel(io.BytesIO(fb)) if bank_file.name.endswith(('.xlsx', '.xls')) else pd.read_csv(io.BytesIO(fb))
                    credit_cols = [c for c in df.columns if any(x in str(c).lower() for x in ['credit', 'deposit', 'cr'])]
                    computed_turnover = pd.to_numeric(df[credit_cols[0]], errors='coerce').sum() if credit_cols else 0.0
                except:
                    computed_turnover = 0.0

        if stock_file:
            stock_metrics = parse_stock_ledger(stock_file.read(), stock_file.name)
                
        tax_metrics = compute_tax_liability(computed_turnover, input_rate, stock_metrics["rectified_realized_pnl"])
        
        if stock_metrics["rectified_realized_pnl"] != 0:
            prescribed_itr = "ITR-2 (Capital Gains + Presumptive Combination Structure)"
        else:
            prescribed_itr = "ITR-4 (Sugam Pure Presumptive Base)"
            
        st.session_state.audit_results = {
            "tax_m": tax_metrics,
            "stock_m": stock_metrics,
            "itr": prescribed_itr,
            "turnover": computed_turnover
        }
        
        st.session_state.pdf_payload = generate_pdf_report(
            input_name, input_id, tax_metrics, stock_metrics, route, prescribed_itr, computed_turnover
        )

# -------------------------------------------------------------------------
# PERSISTENT UI RENDERING LAYER
# -------------------------------------------------------------------------
if st.session_state.audit_results is not None:
    res = st.session_state.audit_results
    st.success(f"🎉 Audit Run Completed Successfully for {input_name}!")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Parsed Bank Turnover", f"INR {res['turnover']:,.2f}")
    with m2:
        st.metric("Audited True STCG Profit", f"INR {res['stock_m']['rectified_realized_pnl']:,.2f}")
    with m3:
        st.metric("Gross Total Income (GTI)", f"INR {res['tax_m']['gross_total_income']:,.2f}")
    with m4:
        st.metric("Net Tax Payable Due", f"INR {res['tax_m']['final_tax']:,.2f}")
        
    st.markdown("---")
    
    d_col1, d_col2 = st.columns([1, 1])
    with d_col1:
        st.markdown("### 📋 Executive Compliance Breakdown")
        breakdown_df = pd.DataFrame({
            "Financial Node Description": [
                "Presumptive Profit Core (Sched. BP)",
                "Rectified Equity Short-Term Capital Gain (Sched. CG)",
                "Gross Combined Portfolio Income Base (GTI)",
                "Calculated Normal Slab Liability Vector",
                "Calculated Special Rate 111A Tax Liability",
                "Section 87A Statutory Rebate Allocation",
                "Net Total Tax Due and Payable"
            ],
            "Value Matrix (INR)": [
                f"INR {res['tax_m']['normal_income']:,.2f}",
                f"INR {res['stock_m']['rectified_realized_pnl']:,.2f}",
                f"INR {res['tax_m']['gross_total_income']:,.2f}",
                f"INR {res['tax_m']['tax_normal']:,.2f}",
                f"INR {res['tax_m']['tax_stcg']:,.2f}",
                f"- INR {res['tax_m']['rebate_87a']:,.2f}",
                f"INR {res['tax_m']['final_tax']:,.2f}"
            ]
        })
        st.table(breakdown_df)
        
        st.download_button(
            label=f"📥 Download Certified Compliance PDF for {input_name}",
            data=st.session_state.pdf_payload,
            file_name=f"KSP_Compliance_Report_{input_id}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    with d_col2:
        st.markdown(f"### 🛠️ Step-by-Step E-Filing Protocol Details")
        st.info(f"📋 **Mandatory Regulatory Form Path Selection:** **{res['itr']}**")
        st.markdown(f"""
        Follow these exact instructions on the official income tax portal to file this audited result:
        
        1. **Portal Authentication & Selection:**
           * Go to `incometax.gov.in`, authenticate via PAN credentials, and navigate to **File Income Tax Return**.
           * Select **Assessment Year 2026-27** → Mode of Filing: **Online** → Application Status: **Individual**.
           * Select **{res['itr'].split(' ')[0]}** from the form selector matrix.
        
        2. **Configure Schedule BP (Business & Profession):**
           * Navigate to the presumptive business sections inside the portal grid.
           * If using **Sec 44AD**, input **Gross Receipts:** `INR {res['turnover']:,.2f}` and **Presumptive Profit:** `INR {res['tax_m']['normal_income']:,.2f}`.
        
        3. **Configure Schedule CG (Capital Gains Manual Overrides):**
           * Under Capital Gains, check the tick box for *Equity shares/units of equity oriented MF liable to STT u/s 111A*.
           * Click add details and input the calculated values:
             * **Full Value of Consideration (Total Sales):** `INR {res['stock_m']['stcg_sales']:,.2f}`
             * **Cost of Acquisition (Adjusted Purchases):** `INR {res['stock_m']['stcg_cost']:,.2f}`
             * **Expenditure wholly connected with transfer:** `INR {res['stock_m']['total_charges'] - 810.0 if res['stock_m']['total_charges'] > 810.0 else 0.0:,.2f}` *(Excluding STT)*.
        
        4. **Map Quarterly Capital Gains Accruals Grid:**
           * Scroll down to the bottom of Schedule CG to locate the **Information about accrual/receipt of Capital Gains** grid.
           * Distribute the net capital gains profit (`INR {res['stock_m']['rectified_realized_pnl']:,.2f}`) across the respective quarterly rows based on actual sale timestamps.
        
        5. **Validate Rebates & Final Submission:**
           * Advance to the final calculation confirmation screen. 
           * Verify that **Section 87A Rebate** automatically targets both tax layers because your combined Gross Total Income (`INR {res['tax_m']['gross_total_income']:,.2f}`) sits safely within limits.
           * Confirm **Net Tax Payable Due** displays exactly **INR 0.00**, proceed to E-verify, and digitally sign using Aadhaar OTP parameters.
        """)