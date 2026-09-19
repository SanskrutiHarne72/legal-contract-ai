"""
services/pdf_generator.py

Professional Legal Contract PDF Generator.
Converts AI-generated contract text (which may contain Markdown) into a
properly structured ReportLab PDF with:
  - Markdown-aware parsing (# headings, **bold**, --- rules, numbered clauses)
  - Per-page header (contract title) and footer (page numbers + disclaimer)
  - Typed, role-specific signature blocks
  - AI-Assisted Draft disclaimer
  - Optional legal-context appendix
"""

import re
from io import BytesIO
from datetime import datetime

from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


# ──────────────────────────────────────────────────────────────────────────────
# Colours & layout constants
# ──────────────────────────────────────────────────────────────────────────────
NAVY   = HexColor("#1C2B4B")
GOLD   = HexColor("#C8972A")
LIGHT  = HexColor("#EDF0F5")
GREY   = HexColor("#6B7280")
BLACK  = HexColor("#1C1C1E")
WHITE  = white

MARGIN  = 1.0 * inch
PAGE_W, PAGE_H = A4
HEADER_H = 0.60 * inch
FOOTER_H = 0.50 * inch


# ──────────────────────────────────────────────────────────────────────────────
# Style definitions
# ──────────────────────────────────────────────────────────────────────────────
def _build_styles() -> dict:
    styles = {}

    styles["doc_title"] = ParagraphStyle(
        "doc_title",
        fontName="Helvetica-Bold",
        fontSize=17,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=4,
        leading=22,
    )
    styles["doc_subtitle"] = ParagraphStyle(
        "doc_subtitle",
        fontName="Helvetica",
        fontSize=9,
        textColor=GREY,
        alignment=TA_CENTER,
        spaceAfter=14,
    )
    # H1 — top-level agreement heading  (# ...)
    styles["h1"] = ParagraphStyle(
        "h1",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=NAVY,
        spaceBefore=20,
        spaceAfter=5,
        leading=17,
    )
    # H2 — major section heading  (## ...)
    styles["h2"] = ParagraphStyle(
        "h2",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=4,
        leading=15,
    )
    # H3 — sub-section / numbered section heading  (### ...)
    styles["h3"] = ParagraphStyle(
        "h3",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=BLACK,
        spaceBefore=10,
        spaceAfter=3,
        leading=14,
    )
    # Body paragraph
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=BLACK,
        leading=14,
        spaceBefore=2,
        spaceAfter=3,
        alignment=TA_JUSTIFY,
    )
    # Sub-clause (indented)  1.1, 2.3 …
    styles["subclause"] = ParagraphStyle(
        "subclause",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=BLACK,
        leading=14,
        spaceBefore=2,
        spaceAfter=3,
        leftIndent=22,
        alignment=TA_JUSTIFY,
    )
    # Centred BETWEEN / AND labels
    styles["between"] = ParagraphStyle(
        "between",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=6,
    )
    # Signature block header
    styles["sig_role"] = ParagraphStyle(
        "sig_role",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=2,
    )
    # Signature field lines
    styles["sig_line"] = ParagraphStyle(
        "sig_line",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=BLACK,
        leading=20,
        spaceBefore=1,
        spaceAfter=1,
    )
    # Disclaimer / legal notice (small italic)
    styles["disclaimer"] = ParagraphStyle(
        "disclaimer",
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=GREY,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=2,
    )
    # Disclaimer heading
    styles["disclaimer_head"] = ParagraphStyle(
        "disclaimer_head",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=GREY,
        spaceBefore=8,
        spaceAfter=2,
    )
    # Blockquote style
    styles["blockquote"] = ParagraphStyle(
        "blockquote",
        fontName="Helvetica-Oblique",
        fontSize=9,
        textColor=NAVY,
        leading=13,
        leftIndent=14,
        spaceBefore=4,
        spaceAfter=4,
    )

    return styles



# ──────────────────────────────────────────────────────────────────────────────
# Header / Footer (drawn on every page via canvas callback)
# ──────────────────────────────────────────────────────────────────────────────
def _make_header_footer(contract_title: str):
    """Return an onPage callback that draws a professional header and footer."""

    def _draw(canv, doc):
        canv.saveState()

        # ── Header bar ────────────────────────────────────────────────────
        canv.setFillColor(NAVY)
        canv.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)

        canv.setFont("Helvetica-Bold", 8.5)
        canv.setFillColor(WHITE)
        short_title = (contract_title.upper()[:70] + "…") if len(contract_title) > 70 else contract_title.upper()
        canv.drawString(MARGIN, PAGE_H - HEADER_H + 0.18 * inch, short_title)

        canv.setFont("Helvetica", 7.5)
        canv.drawRightString(PAGE_W - MARGIN, PAGE_H - HEADER_H + 0.18 * inch, "OFFICIAL DOCUMENT")

        # Gold rule below header
        canv.setStrokeColor(GOLD)
        canv.setLineWidth(1.5)
        canv.line(MARGIN, PAGE_H - HEADER_H - 1, PAGE_W - MARGIN, PAGE_H - HEADER_H - 1)


        # ── Footer bar ────────────────────────────────────────────────────
        canv.setFillColor(LIGHT)
        canv.rect(0, 0, PAGE_W, FOOTER_H, fill=1, stroke=0)

        canv.setFont("Helvetica", 7)
        canv.setFillColor(GREY)
        canv.drawString(MARGIN, 0.16 * inch,
                        "AI Legal Contract Assistant · Not a substitute for professional legal advice")

        canv.setFont("Helvetica-Bold", 7.5)
        canv.drawRightString(PAGE_W - MARGIN, 0.16 * inch, f"Page {doc.page}")

        canv.restoreState()

    return _draw


# ──────────────────────────────────────────────────────────────────────────────
# XML / Inline-Markdown helpers
# ──────────────────────────────────────────────────────────────────────────────
def _esc(text: str) -> str:
    """Escape XML special characters so ReportLab Paragraph won't choke."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def _inline(text: str) -> str:
    """Convert inline Markdown (***bold-italic***, **bold**, *italic*) to RL tags."""
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'\*\*(.*?)\*\*',     r'<b>\1</b>',         text)
    text = re.sub(r'\*(.*?)\*',         r'<i>\1</i>',         text)
    text = re.sub(r'`(.*?)`', r'<font name="Courier" size="8">\1</font>', text)
    return text


def _fmt(raw: str) -> str:
    """Escape XML then apply inline markdown to a raw string."""
    return _inline(_esc(raw))


# ──────────────────────────────────────────────────────────────────────────────
# Markdown → ReportLab flowables
# ──────────────────────────────────────────────────────────────────────────────
_NUMBERED_CLAUSE_RE    = re.compile(r'^\d+\.\s+\S')      # "1. text"
_NUMBERED_SUBCLAUSE_RE = re.compile(r'^\d+\.\d+[\. ]')  # "1.1 text" or "1.1. text"
_BULLET_RE             = re.compile(r'^[-*•] ')
_HR_RE                 = re.compile(r'^[-*_]{3,}$')


def _parse_markdown(text: str, styles: dict) -> list:
    """
    Convert a markdown-flavoured string to ReportLab flowables.
    Handles: # headings, **bold**, --- rules, 1. clauses, 1.1 sub-clauses, bullets.
    """
    flowables = []
    lines = text.split("\n")

    for raw in lines:
        line = raw.strip()

        # ── Blank line ──────────────────────────────────────────────────────
        if not line:
            flowables.append(Spacer(1, 5))
            continue

        # ── H1  (#)  — top-level title/section heading ─────────────────────
        if re.match(r'^# ', line) and not re.match(r'^##', line):
            content = _fmt(line[2:].strip())
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph(content, styles["h1"]))
            continue

        # ── H2  (##) — section heading ──────────────────────────────────────
        if re.match(r'^## ', line) and not re.match(r'^###', line):
            content = _fmt(line[3:].strip())
            flowables.append(Paragraph(content, styles["h2"]))
            continue

        # ── H3  (###) — sub-section heading ────────────────────────────────
        if re.match(r'^### ', line) and not re.match(r'^####', line):
            content = _fmt(line[4:].strip())
            flowables.append(Paragraph(content, styles["h3"]))
            continue

        # ── H4  (####) ──────────────────────────────────────────────────────
        if re.match(r'^#### ', line):
            content = _fmt(line[5:].strip())
            flowables.append(Paragraph(f"<b>{content}</b>", styles["body"]))
            continue

        # ── Blockquote (> text) ──────────────────────────────────────────────
        if line.startswith("> "):
            content = _fmt(line[2:].strip())
            flowables.append(Paragraph(f"<i>{content}</i>", styles["blockquote"]))
            continue

        # ── Table row (| col1 | col2 |) ──────────────────────────────────────
        if line.startswith("|") and line.endswith("|"):
            # Check if this is a header separator row (e.g. |---|---|)
            if re.match(r"^\|[\s\-:|]+\|$", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            # Accumulate table rows or render simple inline grid
            cell_paragraphs = [Paragraph(_fmt(c), styles["body"]) for c in cells]
            # Create a 2-column or N-column table
            from reportlab.platypus import Table, TableStyle
            t = Table([cell_paragraphs], colWidths=[(PAGE_W - 2 * MARGIN) / len(cells)] * len(cells))
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, GREY),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, LIGHT),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            flowables.append(t)
            flowables.append(Spacer(1, 2))
            continue

        # ── Horizontal rule ─────────────────────────────────────────────────
        if _HR_RE.match(line):
            flowables.append(Spacer(1, 6))
            flowables.append(HRFlowable(
                width="100%", thickness=0.6,
                color=GOLD, spaceAfter=6
            ))
            continue

        # ── Numbered sub-clause  1.1 / 2.3.4 etc. ──────────────────────────
        if _NUMBERED_SUBCLAUSE_RE.match(line):
            content = _fmt(line)
            flowables.append(Paragraph(content, styles["subclause"]))
            continue

        # ── Numbered clause  1. / 12. etc. ─────────────────────────────────
        if _NUMBERED_CLAUSE_RE.match(line):
            content = _fmt(line)
            flowables.append(Paragraph(f"<b>{content}</b>", styles["h3"]))
            continue

        # ── Bullet list  - item / * item ────────────────────────────────────
        if _BULLET_RE.match(line):
            content = _fmt(re.sub(r'^[-*•] ', '', line))
            flowables.append(Paragraph(
                f"&nbsp;&nbsp;&nbsp;&bull;&nbsp;&nbsp;{content}",
                styles["body"]
            ))
            continue

        # ── Normal paragraph (handles inline **bold** etc.) ─────────────────
        content = _fmt(line)
        flowables.append(Paragraph(content, styles["body"]))

    return flowables



# ──────────────────────────────────────────────────────────────────────────────
# Signature block
# ──────────────────────────────────────────────────────────────────────────────
_SIG_PARTIES = {
    "Rental Agreement": [
        ("LANDLORD (LESSOR)", "landlord_name"),
        ("TENANT (LESSEE)",   "tenant_name"),
    ],
    "Employment Agreement": [
        ("EMPLOYER",  "employer_name"),
        ("EMPLOYEE",  "employee_name"),
    ],
    "Non Disclosure Agreement (NDA)": [
        ("DISCLOSING PARTY", "disclosing_party"),
        ("RECEIVING PARTY",  "receiving_party"),
    ],
    "Freelance Agreement": [
        ("CLIENT",     "client_name"),
        ("FREELANCER", "freelancer_name"),
    ],
    "Service Agreement": [
        ("CLIENT",           "client_name"),
        ("SERVICE PROVIDER", "provider_name"),
    ],
    "Sale / Purchase Agreement": [
        ("SELLER", "seller_name"),
        ("BUYER",  "buyer_name"),
    ],
    "Partnership Agreement": [
        ("PARTNER 1", "p1_name"),
        ("PARTNER 2", "p2_name"),
    ],
    "Consultancy Agreement": [
        ("CLIENT",     "client_name"),
        ("CONSULTANT", "consultant_name"),
    ],
    "Vendor Agreement": [
        ("PURCHASER", "purchaser_name"),
        ("VENDOR",    "vendor_name"),
    ],
}


def _build_signature_block(
    contract_type: str,
    form_data: dict,
    styles: dict
) -> list:
    """Build a professional typed signature block."""
    flowables = [
        Spacer(1, 24),
        HRFlowable(width="100%", thickness=1.2, color=NAVY, spaceAfter=10),
        Paragraph("SIGNATURES", styles["h1"]),
        Paragraph(
            "IN WITNESS WHEREOF, the parties hereto have executed this Agreement "
            "on the date first written above.",
            styles["body"]
        ),
        Spacer(1, 16),
    ]

    parties = _SIG_PARTIES.get(
        contract_type,
        [
            ("PARTY A", "custom_party_a_name"),
            ("PARTY B", "custom_party_b_name"),
        ],
    )

    for role, key in parties:
        name = _esc(form_data.get(key, f"[{role}]") or f"[{role}]")
        block = KeepTogether([
            Paragraph(f"<b>{role}</b>", styles["sig_role"]),
            Paragraph(f"Name:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{name}", styles["sig_line"]),
            Paragraph("Signature:&nbsp;&nbsp;_________________________________", styles["sig_line"]),
            Paragraph("Date:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_________________________________", styles["sig_line"]),
            Spacer(1, 18),
        ])
        flowables.append(block)

    return flowables


# ──────────────────────────────────────────────────────────────────────────────
# AI-Assisted disclaimer
# ──────────────────────────────────────────────────────────────────────────────
def _build_disclaimer(styles: dict) -> list:
    return [
        Spacer(1, 20),
        HRFlowable(width="100%", thickness=0.5, color=GREY, spaceAfter=6),
        Paragraph("AI-ASSISTED DRAFT", styles["disclaimer_head"]),
        Paragraph(
            "This document has been generated using an AI-assisted legal drafting system "
            "based on the information provided by the user and available legal context. "
            "It is NOT a guarantee of legal validity and should be reviewed by an "
            "appropriately qualified legal professional before execution or use. "
            "The AI system does not provide legal advice.",
            styles["disclaimer"]
        ),
        Paragraph(
            "Human / legal review is recommended before execution or use.",
            styles["disclaimer"]
        ),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Legal references appendix
# ──────────────────────────────────────────────────────────────────────────────
def _build_legal_refs(legal_context: list, styles: dict) -> list:
    if not legal_context:
        return []
    flowables = [
        Spacer(1, 14),
        Paragraph("LEGAL CONTEXT USED", styles["h2"]),
    ]
    for ref in legal_context:
        act      = _esc(ref.get("law_act", ""))
        section  = _esc(ref.get("section", ""))
        topic    = _esc(ref.get("topic", ""))
        source   = _esc(ref.get("source", ""))
        verified = _esc(ref.get("last_verified", ""))
        status   = _esc(ref.get("status", ""))

        label = f"&bull; <b>{act}</b>"
        if section:
            label += f", {section}"
        if topic:
            label += f" — {topic}"
        if status:
            label += f" <i>({status})</i>"

        flowables.append(Paragraph(label, styles["disclaimer"]))
        if source:
            flowables.append(Paragraph(
                f"&nbsp;&nbsp;&nbsp;&nbsp;Source: {source}"
                + (f"&nbsp;|&nbsp;Verified: {verified}" if verified else ""),
                styles["disclaimer"]
            ))
    return flowables


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────
def create_pdf(
    contract_text: str,
    contract_title: str = "Legal Agreement",
    contract_type: str = "",
    form_data: dict = None,
    legal_context: list = None,
) -> bytes:
    """
    Generate a professional legal PDF from contract text.

    Args:
        contract_text:  Raw contract text (may contain Markdown).
        contract_title: Human-readable title shown in header and title block.
        contract_type:  Contract type string (used for signature block lookup).
        form_data:      User-supplied form values (used for typed signatures).
        legal_context:  List of legal reference dicts (from legal_data layer).

    Returns:
        PDF file as bytes.
    """
    form_data    = form_data    or {}
    legal_context = legal_context or []

    buffer = BytesIO()
    styles = _build_styles()

    # ── Page frame (inside header + footer margins) ──────────────────────────
    content_frame = Frame(
        MARGIN,
        FOOTER_H + 0.08 * inch,
        PAGE_W - 2 * MARGIN,
        PAGE_H - HEADER_H - FOOTER_H - 0.16 * inch,
        id="main",
        leftPadding=0,
        rightPadding=0,
        topPadding=4,
        bottomPadding=4,
    )

    hf_callback = _make_header_footer(contract_title)

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_H + 0.12 * inch,
        bottomMargin=FOOTER_H + 0.12 * inch,
        title=contract_title,
        author="AI Legal Contract Assistant",
        subject=contract_type,
        creator="AI Legal Contract Assistant v2.5",
    )
    doc.addPageTemplates([
        PageTemplate(
            id="main_template",
            frames=[content_frame],
            onPage=hf_callback,
        )
    ])

    # ── Story ────────────────────────────────────────────────────────────────
    story = []

    # Title block
    story.append(Spacer(1, 8))
    story.append(Paragraph(_esc(contract_title.upper()), styles["doc_title"]))
    today = datetime.now().strftime("%d %B %Y")
    story.append(Paragraph(f"Prepared: {today}", styles["doc_subtitle"]))
    story.append(HRFlowable(
        width="55%", thickness=2, color=GOLD,
        spaceBefore=4, spaceAfter=14
    ))

    # Main contract body (markdown-aware)
    story.extend(_parse_markdown(contract_text, styles))

    # Signature block — only if contract text doesn't already contain one
    _sig_markers = ("in witness whereof", "signature:", "signed by", "witnessed by")
    has_sig = any(m in contract_text.lower() for m in _sig_markers)
    if not has_sig:
        story.extend(_build_signature_block(contract_type, form_data, styles))

    # Legal references appendix (only if data supplied)
    if legal_context:
        story.extend(_build_legal_refs(legal_context, styles))

    # AI-assisted disclaimer (only for review/analysis reports, not formal agreement body)
    if "report" in contract_type.lower() or "review" in contract_type.lower() or "explanation" in contract_type.lower():
        story.extend(_build_disclaimer(styles))

    # ── Build ────────────────────────────────────────────────────────────────

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes