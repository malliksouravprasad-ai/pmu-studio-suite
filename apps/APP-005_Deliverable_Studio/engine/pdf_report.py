"""PDF report generator for APP-008 (reportlab)."""
import io
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from .deliverable_model import ReportConfig, SectionDef

_NAVY   = colors.HexColor("#1F3864")
_LIGHT  = colors.HexColor("#D9E1F2")
_TOTAL  = colors.HexColor("#BDD7EE")
_GREY   = colors.HexColor("#595959")

_PAGE_W, _PAGE_H = A4


def _styles():
    ss = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PMUTitle", parent=ss["Title"],
        fontSize=22, textColor=_NAVY, spaceAfter=6, leading=26)
    meta_style = ParagraphStyle(
        "PMUMeta", parent=ss["Normal"],
        fontSize=10, textColor=_GREY, spaceAfter=3)
    h1_style = ParagraphStyle(
        "PMUH1", parent=ss["Heading1"],
        fontSize=14, textColor=_NAVY, spaceAfter=6, spaceBefore=12,
        borderPad=4, leading=18)
    body_style = ParagraphStyle(
        "PMUBody", parent=ss["Normal"],
        fontSize=10, spaceAfter=6, leading=14)
    return title_style, meta_style, h1_style, body_style


def _df_to_table(df: pd.DataFrame) -> Table:
    if df.empty:
        return Paragraph("(No data available.)", getSampleStyleSheet()["Normal"])

    header = [str(c) for c in df.columns]
    rows   = [[str(v) if pd.notna(v) else "" for v in row]
              for _, row in df.iterrows()]
    data   = [header] + rows

    col_count = len(header)
    avail_w   = _PAGE_W - 4 * cm
    col_w     = avail_w / col_count

    style = TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), _NAVY),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#AAAAAA")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT]),
        ("ALIGN",       (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ])

    # Highlight TOTAL row
    for ri, row in enumerate(rows, start=1):
        if row and row[0] == "TOTAL":
            style.add("BACKGROUND", (0, ri), (-1, ri), _TOTAL)
            style.add("FONTNAME",   (0, ri), (-1, ri), "Helvetica-Bold")

    t = Table(data, colWidths=[col_w] * col_count, repeatRows=1)
    t.setStyle(style)
    return t


def save_pdf_report(
    section_data: dict, config: ReportConfig, artifact_id: str
) -> tuple:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
    )

    title_style, meta_style, h1_style, body_style = _styles()
    story = []

    # Cover
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(config.report_title, title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=_NAVY, spaceAfter=8))

    for label, value in [
        ("Programme",    config.programme),
        ("Organisation", config.organization),
        ("Prepared by",  config.author),
        ("Date",         config.report_date),
    ]:
        if value:
            story.append(Paragraph(f"<b>{label}:</b> {value}", meta_style))

    if config.description:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(config.description, body_style))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"<i>Artifact ID: {artifact_id}</i>",
                            ParagraphStyle("ArtID", parent=meta_style, fontSize=8)))
    story.append(PageBreak())

    # Sections
    for sdef in config.sections:
        if not sdef.enabled:
            continue

        story.append(Paragraph(sdef.title, h1_style))
        story.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#AAAAAA"), spaceAfter=6))

        if sdef.section_type == "narrative":
            if sdef.narrative:
                story.append(Paragraph(sdef.narrative, body_style))
        else:
            if sdef.narrative:
                story.append(Paragraph(sdef.narrative, body_style))
            df = section_data.get(sdef.section_id, pd.DataFrame())
            story.append(_df_to_table(df))

        story.append(Spacer(1, 0.8 * cm))

    doc.build(story)
    buf.seek(0)
    fname = f"{artifact_id}_report.pdf"
    return fname, buf
