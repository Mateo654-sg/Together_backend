"""
Generador de exportación CSV (FR-097).

Usa el módulo estándar csv.
"""

import csv
import io
from decimal import Decimal


def generate_csv(rows: list[dict]) -> bytes:
    """Genera el contenido CSV de los movimientos.

    Args:
        rows: Filas de movimientos (date, type, category, description, amount).

    Returns:
        Bytes del archivo CSV (UTF-8 con BOM para Excel).
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Fecha", "Tipo", "Categoría", "Descripción", "Monto"])
    for row in rows:
        amount: Decimal = row["amount"]
        writer.writerow(
            [
                row["date"],
                row["type"],
                row["category"],
                row["description"],
                f"{amount:.2f}".replace(".", ","),
            ]
        )
    return buffer.getvalue().encode("utf-8-sig")
