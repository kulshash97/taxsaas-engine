def parse_bank_statement_credits(text):
    """Aggressive parser scanning for nearly all Indian banking layout credit strings."""
    if not text:
        return 0.0
    clean_text = text.replace(',', '')
    patterns = [
        r"Total\s+Credits?[\s\S]{0,40}?([\d]+\.\d{2})",
        r"Total\s+Deposit(?:s)?[\s\S]{0,40}?([\d]+\.\d{2})",
        r"Credit\s+Summation[\s\S]{0,30}?([\d]+\.\d{2})",
        r"Total\s+Cr[\.\s]+([\d]+\.\d{2})",
        r"SUM\s+OF\s+CREDITS[\s\S]{0,30}?([\d]+\.\d{2})",
        r"Total\s+Inflows?[\s\S]{0,30}?([\d]+\.\d{2})",
        r"Transaction\s+Total\s+Cr[\s\S]{0,20}?([\d]+\.\d{2})"
    ]
    for pattern in patterns:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        if matches:
            try: return float(re.sub(r'[^\d.]', '', matches[-1]))
            except ValueError: continue
    return 0.0

def parse_ais_turnover(text):
    """Aggressive parser searching for specialized AIS/TDS information statement schedules."""
    if not text:
        return 0.0
    clean_text = text.replace(',', '')
    patterns = [
        r"Business\s+receipts[\s\S]{0,50}?([\d]+\.\d{2})",
        r"Receipts\s+under\s+Section\s+194J[\s\S]{0,50}?([\d]+\.\d{2})",
        r"Total\s+Value\s*[\s:;]+\s*([\d]+\.\d{2})",
        r"Amount\s+Paid/Credited[\s\S]{0,40}?([\d]+\.\d{2})",
        r"Gross\s+Salary[\s\S]{0,30}?([\d]+\.\d{2})",
        r"Information\s+Value\s*[\s:;]+\s*([\d]+\.\d{2})"
    ]
    for pattern in patterns:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        if matches:
            try: return float(re.sub(r'[^\d.]', '', matches[-1]))
            except ValueError: continue
    return 0.0