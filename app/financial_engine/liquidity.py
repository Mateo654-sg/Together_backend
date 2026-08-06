"""
Motor 5: Liquidez.

Liquidez = Saldo Disponible / Gastos Promedio Mensuales.
"""

from decimal import Decimal

from app.financial_engine.utils import ZERO, as_decimal


def liquidity_ratio(available_balance, average_monthly_expense) -> Decimal:
    """Calcula el índice de liquidez (meses de gastos cubiertos por el saldo)."""
    if as_decimal(average_monthly_expense) <= ZERO:
        return ZERO
    return as_decimal(available_balance) / as_decimal(average_monthly_expense)


def classify_liquidity(ratio: Decimal) -> str:
    """Clasifica la liquidez: Excelente, Buena, Aceptable o Crítica."""
    if ratio >= Decimal("6"):
        return "Excelente"
    if ratio >= Decimal("3"):
        return "Buena"
    if ratio >= Decimal("1"):
        return "Aceptable"
    return "Crítica"
