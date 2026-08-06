"""
Motor 4 y 6: Cash Flow y Burn Rate.

Flujo neto = Ingresos - Gastos.
Burn rate = Gastos / Días.
"""

from decimal import Decimal

from app.financial_engine.utils import ZERO, as_decimal


def net_cash_flow(total_income, total_expense) -> Decimal:
    """Calcula el flujo de caja neto (ingresos - gastos)."""
    return as_decimal(total_income) - as_decimal(total_expense)


def classify_cash_flow(flow: Decimal) -> str:
    """Clasifica el flujo de caja: Positivo, Negativo o Neutro."""
    if flow > ZERO:
        return "Positivo"
    if flow < ZERO:
        return "Negativo"
    return "Neutro"


def burn_rate(total_expense, days: int) -> Decimal:
    """Calcula la velocidad de consumo del dinero (gastos por día)."""
    if days <= 0:
        return ZERO
    return as_decimal(total_expense) / days
