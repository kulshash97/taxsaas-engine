import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_marketing_flyer():
    pdf_filename = "KSP_Platform_ROI_Flyer.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    # Premium Corporate Executive Palette
    primary_luxury = colors.HexColor('#0F172A') # Dark Slate Navy
    accent_purple = colors.HexColor('#6D28D9') # Elite Violet
    text_dark = colors.HexColor('#1E293B')
    
    title_style = ParagraphStyle('M1', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=primary_luxury, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('M2', fontName='Helvetica', fontSize=11, leading=15, textColor=colors.HexColor('#4B5563'), alignment=TA_CENTER)
    section_heading = ParagraphStyle('M3', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=accent_purple, alignment=TA_LEFT)
    body_style = ParagraphStyle('M4', fontName='Helvetica', fontSize=10, leading=14, textColor=text_dark, alignment=TA_LEFT)
    
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.white, alignment=TA_LEFT)
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=9, leading=12, textColor=text_dark, alignment=TA_LEFT)
    td_bold = ParagraphStyle('TDB', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=accent_purple, alignment=TA_LEFT)

    story = [
        Paragraph("KSP CONSOLE PLATFORM V3.0", title_style),
        Paragraph("The Algorithmic Financial Intelligence Node Built Exclusively for Indian CA Practices", subtitle_style),
        Spacer(1, 20),
        
        Paragraph("🚀 THE VALUE PROPOSITION: OPERATIONAL LEVERAGE", section_heading),
        Spacer(1, 6),
        Paragraph("Stop burning costly senior staff or article hours on manual workbook compilation, template styling, or parsing compliance boundary limits. The KSP Unified Console automates advanced statutory filing analysis, dynamic business evaluations, and predictive fractional CFO model generation in under 2 seconds. Move your practice up the value chain from commodity compliance to high-margin advisory mandates.", body_style),
        Spacer(1, 15),
        
        Paragraph("📊 MULTI-TENANT SUBSCRIPTION PLATFORM STRUCTURE", section_heading),
        Spacer(1, 6)
    ]
    
    # Table data matrix using standard INR syntax to avoid system font bugs or square blocks
    table_data = [
        [Paragraph("Operational Platform Tier", th_style), Paragraph("Monthly Software Access", th_style), Paragraph("Core Active Modules Included", th_style), Paragraph("Estimated Billable Firm ROI", th_style)],
        [Paragraph("🟢 Starter Solo Tier", td_bold), Paragraph("INR 1,999 / Month", td_style), Paragraph("Module 1: Smart ITR Filing Engine<br/>Module 2: Incorporation Strategy Matrix", td_style), Paragraph("Recovers entire tool cost using just one micro-advisory optimization brief filing."),],
        [Paragraph("🔵 Growth Practice Tier", td_bold), Paragraph("INR 4,999 / Month", td_style), Paragraph("All Modules 1 & 2 +<br/>Module 5: GST Command Center Core<br/>Module 6: Predictive Fractional CFO Model", td_style), Paragraph("Enables junior staff to cleanly service premium INR 25k - INR 75k/mo localized CFO retainers."),],
        [Paragraph("👑 Elite Partner Tier", td_bold), Paragraph("INR 9,999 / Month", td_style), Paragraph("Complete 6-Module Infrastructure Suite Unleashed<br/>Includes Auto Valuation Modeler & Venture Pitch Deck Architect", td_style), Paragraph("Unlocks immediate capabilities to command INR 50,000+ Corporate valuation fees seamlessly.")]
    ]
    
    t = Table(table_data, colWidths=[110, 110, 190, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_luxury),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
    ]))
    
    story.append(t)
    Spacer(1, 20)
    
    # Contact CTA block dynamically configured to match your live sender inbox
    story.append(Paragraph("💼 SECURE YOUR PRACTICE NODE TODAY", section_heading))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Enterprise Request Pipeline:</b> Deploy our secure multi-tenant network inside your firm infrastructure today. Brand your deliverables, lock in automated internal controls, and run live validation reports seamlessly. Connect directly via <b>shashankkulkarni228@gmail.com</b> to configure your firm access keys.", body_style))
    
    doc.build(story)
    print(f"📁 Professional PDF Marketing Flyer built successfully as: '{pdf_filename}'")

if __name__ == "__main__":
    generate_marketing_flyer()