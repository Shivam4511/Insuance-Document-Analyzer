import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# output dir
out_dir = "test_samples"
os.makedirs(out_dir, exist_ok=True)

styles = getSampleStyleSheet()
title_style = styles['Title']
h1_style = styles['Heading1']
h2_style = styles['Heading2']
normal_style = styles['Normal']

def create_policy_pdf(filename, title, company_name, sections, is_compliant=True):
    doc = SimpleDocTemplate(os.path.join(out_dir, filename), pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    Story = []
    
    # Header
    Story.append(Paragraph(f"<b>{company_name}</b>", title_style))
    Story.append(Paragraph(title, h2_style))
    Story.append(Spacer(1, 0.2 * inch))
    
    # Table for policy details
    data = [
        ['Policy No:', 'POL-2026-88992' + str(len(sections))],
        ['Insured Name:', 'John Doe'],
        ['Vehicle No:', 'MH-12-AB-1234'],
        ['Policy Period:', '01-Apr-2026 to 31-Mar-2027']
    ]
    t = Table(data, colWidths=[2*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    Story.append(t)
    Story.append(Spacer(1, 0.5 * inch))

    # Add sections based on compliance
    for heading, content in sections:
        Story.append(Paragraph(f"<b>{heading}</b>", h1_style))
        Story.append(Spacer(1, 0.1 * inch))
        Story.append(Paragraph(content, normal_style))
        Story.append(Spacer(1, 0.2 * inch))
        
    # Footer disclaimer
    Story.append(Spacer(1, 1 * inch))
    Story.append(Paragraph("<i>This is a computer generated document.</i>", styles['Italic']))

    doc.build(Story)
    print(f"Created: {filename}")


# --- Sample 1: Fully Compliant ---
sections_1 = [
    ("COVERAGE", "This policy provides comprehensive coverage including Own Damage and mandatory Third Party Liability as per the Motor Vehicles Act 1988. The IDV is fixed at Rs. 5,00,000."),
    ("CANCELLATION", "The policy may be cancelled by the insured by giving 7 days notice. Refund of premium will be computed on short period rates, provided no claim has occurred during the current policy period."),
    ("EXCLUSIONS", "The company shall not be liable for any claim arising out of driving under the influence of intoxicating liquor or drugs."),
    ("GRIEVANCE", "In case of any grievance, the insured may approach the Grievance Redressal Officer of the company or the Insurance Ombudsman as per IRDAI guidelines.")
]
create_policy_pdf("Sample1_Compliant.pdf", "Motor Insurance Policy", "Safeguard General Insurance Ltd.", sections_1, True)


# --- Sample 2: Non-Compliant (No Refund) ---
sections_2 = [
    ("COVERAGE", "This policy covers Third Party Liability and Own Damage up to the limits specified in the schedule."),
    ("CANCELLATION", "This policy cannot be cancelled by the policyholder midway through the term. Absolutely no refund of premium will be provided if cancellation is initiated by the insured under any circumstances. The company reserves the sole right to cancel the policy."),
    ("CLAIMS", "Claims must be intimated strictly within 24 hours of the accident, failing which the claim stands totally repudiated.")
]
create_policy_pdf("Sample2_NoRefund.pdf", "Two Wheeler Insurance", "Apex Insurance Co.", sections_2, False)


# --- Sample 3: Non-Compliant (Exorbitant Deductible & Unfair clauses) ---
sections_3 = [
    ("COVERAGE", "Standard Comprehensive Coverage for Private Car."),
    ("DEDUCTIBLES", "A mandatory compulsory deductible of Rs. 25,000 applies to every single claim filed under Own Damage section irrespective of the vehicle class or IRDAI standard deductibles."),
    ("DEPRECIATION", "The company will apply a flat 60% depreciation on all parts (plastic, glass, rubber, and metal) from day one, regardless of the age of the vehicle.")
]
create_policy_pdf("Sample3_HighDeductible.pdf", "Private Car Package Policy", "SecureDrive Insurance", sections_3, False)


# --- Sample 4: Non-Compliant (Third Party missing/limited) ---
sections_4 = [
    ("COVERAGE", "This policy provides Own Damage coverage. Due to the high risk nature of the vehicle, Third Party Liability coverage is entirely excluded from this policy and must be procured separately."),
    ("EXCLUSIONS", "The insurer will not cover damages if the vehicle was driven by any person other than the registered owner, even if they hold a valid driving license."),
    ("CANCELLATION", "Refund of premium upon cancellation is solely at the discretion of the branch manager.")
]
create_policy_pdf("Sample4_MissingTP.pdf", "Commercial Vehicle Policy", "Transit Guard Insurance", sections_4, False)

# --- Sample 5: Ambiguous / Borderline ---
sections_5 = [
    ("COVERAGE", "Coverage is provided subject to the terms herein. The company covers sudden drops in IDV without notice."),
    ("CLAIMS PROCEDURE", "In the event of a total loss, the claim settlement amount will be decided mutually, but the company’s decision shall be final and binding. The original IDV mentioned in the schedule is merely indicative and subject to change at the time of claim."),
    ("GRIEVANCE", "Complaints must be filed only via written letter to the registered corporate office.")
]
create_policy_pdf("Sample5_Ambiguous.pdf", "Standard Motor Policy", "Reliant Insurance Ltd.", sections_5, False)
