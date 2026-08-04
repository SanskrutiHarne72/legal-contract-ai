from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


def create_pdf(contract_text):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]

    body_style = styles["BodyText"]

    story = []

    story.append(Paragraph("AI LEGAL CONTRACT", title_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Generated using AI Legal Contract Assistant", heading_style))
    story.append(Spacer(1, 20))

    for line in contract_text.split("\n"):

        if line.strip() == "":
            story.append(Spacer(1, 10))
        else:
            story.append(
                Paragraph(
                    line.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;"),
                    body_style
                )
            )

    story.append(Spacer(1, 30))

    story.append(Paragraph("<b>Party A Signature:</b> ____________________", heading_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Party B Signature:</b> ____________________", heading_style))
    story.append(Spacer(1, 20))

    doc.build(story)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf