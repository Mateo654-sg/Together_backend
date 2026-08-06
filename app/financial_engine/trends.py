"""
Motor 15 y 16: Spending Trend y Category Dominance.

Tendencia: compara promedios recientes contra históricos.
Dominancia: Categoría / Gasto Total.
"""

from decimal import Decimal

from app.financial_engine.utils import ZERO, as_decimal, safe_percentage


def spending_trend(recent_average: Decimal, historical_average: Decimal) -> str:
    """Clasifica la tendencia de gasto: Creciente, Estable o Decreciente."""
    if as_decimal(historical_average) <= ZERO:
        return "Estable"
    delta = (as_decimal(recent_average) - as_decimal(historical_average)) / as_decimal(
        historical_average
    )
    if delta > Decimal("0.10"):
        return "Creciente"
    if delta < Decimal("-0.10"):
        return "Decreciente"
    return "Estable"


def category_dominance(category_amount, total_expense) -> Decimal:
    """Calcula el porcentaje que representa una categoría del gasto total (0-100)."""
    return safe_percentage(as_decimal(category_amount), as_decimal(total_expense))


def top_categories(category_totals: dict[str, Decimal]) -> list[dict]:
    """Devuelve categorías ordenadas por monto con su porcentaje del total."""
    if not category_totals:
        return []
    total = sum(as_decimal(v) for v in category_totals.values())
    if total <= ZERO:
        return []
    ranked = [
        {
            "category": name,
            "total": float(as_decimal(amount)),
            "percentage": float(safe_percentage(as_decimal(amount), total)),
        }
        for name, amount in category_totals.items()
    ]
    return sorted(ranked, key=lambda item: item["total"], reverse=True)
