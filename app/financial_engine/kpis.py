"""
Motor 7, 17 y 18: Saving Rate, Weekly Average y Monthly Average.

Saving rate = Ahorro / Ingresos * 100.
Promedios = Total / Períodos.
"""

from decimal import Decimal

from app.financial_engine.utils import ZERO, as_decimal, safe_percentage


def savings_rate(total_income, total_expense) -> Decimal:
    """Calcula la tasa de ahorro porcentual (0-100)."""
    savings = as_decimal(total_income) - as_decimal(total_expense)
    return safe_percentage(savings, as_decimal(total_income))


def classify_savings_rate(rate: Decimal) -> str:
    """Clasifica la tasa de ahorro.

    Excelente > 30%, Buena 20-30%, Regular 10-20%, Crítica < 10%.
    """
    if rate > Decimal("30"):
        return "Excelente"
    if rate > Decimal("20"):
        return "Buena"
    if rate > Decimal("10"):
        return "Regular"
    return "Crítica"


def expense_ratio(total_expense, total_income) -> Decimal:
    """Calcula la proporción de gastos sobre ingresos (0-100)."""
    return safe_percentage(as_decimal(total_expense), as_decimal(total_income))


def weekly_average(total_amount, weeks: int) -> Decimal:
    """Calcula el promedio semanal (total / semanas)."""
    if weeks <= 0:
        return ZERO
    return as_decimal(total_amount) / weeks


def monthly_average(total_amount, months: int) -> Decimal:
    """Calcula el promedio mensual (total / meses)."""
    if months <= 0:
        return ZERO
    return as_decimal(total_amount) / months
