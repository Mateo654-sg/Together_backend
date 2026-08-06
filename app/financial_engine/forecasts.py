"""
Motor 19 y 20: Year Projection y Forecast Engine.

Proyección a fin de año: saldo, gastos y ahorro.
Forecast: saldo futuro, metas, liquidez y presupuesto. Solo matemáticas.
"""

from datetime import date

from decimal import Decimal

from app.financial_engine.kpis import monthly_average
from app.financial_engine.utils import ZERO, as_decimal


def year_projection(
    total_income, total_expense, start_month: int, year: int, today: date | None = None
) -> dict:
    """Proyecta saldo, gastos y ahorro al finalizar el año.

    Extrapola el promedio mensual por los meses restantes del año.
    """
    today = today or date.today()
    months_elapsed = max(start_month, 1)
    months_remaining = max(12 - months_elapsed, 0)

    monthly_income = monthly_average(total_income, months_elapsed)
    monthly_expense = monthly_average(total_expense, months_elapsed)
    monthly_savings = monthly_income - monthly_expense

    projected_income = as_decimal(total_income) + monthly_income * months_remaining
    projected_expense = as_decimal(total_expense) + monthly_expense * months_remaining
    projected_balance = projected_income - projected_expense
    projected_savings = monthly_savings * (months_elapsed + months_remaining)

    return {
        "year": year,
        "months_elapsed": months_elapsed,
        "months_remaining": months_remaining,
        "projected_income": projected_income,
        "projected_expense": projected_expense,
        "projected_balance": projected_balance,
        "projected_savings": projected_savings,
    }


def forecast_balance(current_balance, monthly_savings, months: int) -> Decimal:
    """Calcula el saldo futuro tras N meses con un ahorro mensual constante."""
    if months < 0:
        return ZERO
    return as_decimal(current_balance) + as_decimal(monthly_savings) * months
