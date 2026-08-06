"""
Generador de exportación PDF (FR-095).

Usa reportlab para producir un PDF con tabla de movimientos.
"""

from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _format_amount(value) -> str:
    if isinstance(value, Decimal):
        return f"${value:,.2f}".replace(",", ".")
    return f"${float(value):,.2f}"


def generate_pdf(rows: list[dict], title: str = "Movimientos Financieros") -> bytes:
    """Genera el contenido del PDF de los movimientos.

    Args:
        rows: Filas de movimientos (date, type, category, description, amount).
        title: Título del documento.

    Returns:
        Bytes del archivo PDF.
    """
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ExportTitle",
        parent=styles["Title"],
        fontSize=16,
        leading=20,
        spaceAfter=12,
    )

    elements = [Paragraph(title, title_style)]

    data = [["Fecha", "Tipo", "Categoría", "Descripción", "Monto"]]
    for row in rows:
        data.append(
            [
                row["date"],
                row["type"],
                row["category"],
                row["description"],
                _format_amount(row["amount"]),
            ]
        )

    table = Table(data, colWidths=[25 * mm, 22 * mm, 30 * mm, 70 * mm, 35 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                ("ALIGN", (4, 0), (4, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(Spacer(1, 8))
    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()
