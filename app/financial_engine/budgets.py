"""
Motor 8: Budget Consumption.

Consumo = Gastado / Presupuesto * 100.

Alertas: 80%, 90%, 100%, 120%.
"""

from decimal import Decimal


from app.financial_engine.utils import as_decimal, safe_percentage


def budget_consumption(spent, budget) -> Decimal:
    """Calcula el porcentaje de presupuesto consumido (0-100+)."""
    return safe_percentage(as_decimal(spent), as_decimal(budget))


def budget_alert_level(consumption: Decimal) -> int:
    """Devuelve el umbral de alerta superado (80, 90, 100, 120) o 0 si ninguno."""
    for threshold in (Decimal("120"), Decimal("100"), Decimal("90"), Decimal("80")):
        if consumption >= threshold:
            return int(threshold)
    return 0
