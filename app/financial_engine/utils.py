"""
Utilidades compartidas del Financial Rules Engine.

Funciones de soporte para cálculos determinísticos y auditables.
"""

from decimal import Decimal

ZERO = Decimal("0")


def as_decimal(value) -> Decimal:
    """Convierte un valor numérico a Decimal de forma segura."""
    return Decimal(str(value))


def clamp(value: Decimal, low: Decimal, high: Decimal) -> Decimal:
    """Acota un valor entre low y high."""
    return min(max(value, low), high)


def safe_percentage(part: Decimal, total: Decimal) -> Decimal:
    """Calcula part/total*100 evitando división por cero."""
    if total <= ZERO:
        return ZERO
    return clamp(part / total * 100, ZERO, Decimal("100"))


def months_between(start_year: int, start_month: int, end_year: int, end_month: int) -> int:
    """Número de meses completos entre dos períodos (>= 1)."""
    months = (end_year - start_year) * 12 + (end_month - start_month)
    return max(months, 1)
