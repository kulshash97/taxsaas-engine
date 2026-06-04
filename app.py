# ─────────────────────────────────────────────
#  FULL RENDERING MODULE FOR ITR SUITE
# ─────────────────────────────────────────────
def render_itr_module(user):
    st.title("Interactive Tax & Optimization Suite")
    st.markdown(f"**Firm Instance:** `{user['firm']}` | **Tier:** `{user['plan']}`")
    st.info("Upload structural bank statements or asset ledgers to trigger automated ingestion routing.")
    
    # Grid layout for Core Ingestion Data
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">1. Client Meta Records</div>', unsafe_allow_html=True)
        c_name = st.text_input("Assessee Legal Name", value="Shashank Kulkarni")
        c_pan = st.text_input("Permanent Account Number (PAN)", max_chars=10, value="ABCDE1234F")
        
        st.markdown('<div class="section-header">2. Statement Ingestion Parsers</div>', unsafe_allow_html=True)
        bank_file = st.file_uploader("Upload Bank Statement (PDF, Excel, CSV)", type=["pdf", "xlsx", "xls", "csv"])
        ledger_file = st.file_uploader("Upload Capital Gains Stock Ledger", type=["pdf", "xlsx", "xls", "csv"])
        
        # Real-time Background Parsing Processing
        if bank_file:
            amt, parser_used = UniversalBankParser.parse(bank_file)
            st.session_state.parsed_gross = amt
            st.success(f"Parser Engine Applied: Gross credits extracted — ₹ {amt:,.2f}")
            
        if ledger_file:
            cg_data = StockLedgerParser.parse(ledger_file)
            st.session_state.parsed_stcg = cg_data["stcg_111a"] + cg_data["stcg_other"]
            st.session_state.parsed_ltcg = cg_data["ltcg_112a"] + cg_data["ltcg_other"]
            st.success("Stock ledger metrics cleanly mapped to corresponding schedules.")

    with col2:
        st.markdown('<div class="section-header">3. Manual Adjustments & Schedule Flags</div>', unsafe_allow_html=True)
        gross_receipts = st.number_input("Gross Receipts / Turnover (INR)", value=float(st.session_state.parsed_gross), step=10000.0)
        salary_inc = st.number_input("Salary Income (INR)", value=0.0, step=5000.0)
        other_inc = st.number_input("Income from Other Sources (INR)", value=0.0, step=5000.0)
        deductions = st.number_input("Chapter VIA Deductions (Old Regime)", value=0.0, step=5000.0)
        
        st.markdown("**Compliance Strategy Risk Flags**")
        is_dir = st.checkbox("Holds directorship or unlisted equity shares")
        f_assets = st.checkbox("Maintains foreign bank accounts / assets (Schedule FA)")
        agri_flag = st.checkbox("Agricultural income exceeds ₹5,000 threshold")

    st.markdown("---")
    
    # Execution Architecture Control Elements
    route_choice = st.selectbox("Execution Route Mapping Engine", ["Standard Route (Normal Provision Summary)", "Section 44AD (Presumptive Business)", "Section 44ADA (Presumptive Professional)"])
    regime_choice = st.selectbox("Tax Code Regime Selection", ["NEW", "OLD"])
    
    if st.button("Execute Tax Computation Matrix"):
        # Instantiate engine instance running context models
        engine = TaxEngine()
        engine.gross_receipts = gross_receipts
        engine.salary_income = salary_inc
        engine.other_sources_income = other_inc
        engine.total_deductions = deductions
        engine.is_director = is_dir
        engine.has_foreign_assets = f_assets
        engine.has_agri_over_5k = agri_flag
        
        # If stock ledger data was parsed, link fields to internal variables
        if ledger_file:
            engine.stcg_111a = cg_data["stcg_111a"]
            engine.stcg_other = cg_data["stcg_other"]
            engine.ltcg_112a = cg_data["ltcg_112a"]
            engine.ltcg_other = cg_data["ltcg_other"]

        # Calculate standard compliance
        result = engine.compute(route=route_choice, regime=regime_choice)
        st.session_state.last_itr_result = result
        
        # Display live dashboard cards to terminal screen
        st.success(f"Processing Complete: Assigned Form {result['assigned_form']}")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown("### Summary Metrics")
            for k, v in result["metrics"].items():
                st.text(f"{k}: ₹ {v:,.2f}")
        with m_col2:
            st.markdown("### Final Tax Computations")
            for k, v in result["tax_breakdown"].items():
                st.text(f"{k}: ₹ {v:,.2f}")
                
        # Generate the live PDF bytes for client download
        pdf_bytes = generate_itr_pdf(c_name, c_pan, user['firm'], result)
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"KSP_TaxReport_{c_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )