"""
Motor 10 (aplicado a predicciones) y Forecast Engine.

Predicciones matemáticas de ahorro, cumplimiento de metas, flujo de caja
y saldo. Nunca utiliza IA.
"""

from datetime import date

from app.financial_engine.goals import goal_forecast_months
from app.financial_engine.utils import ZERO, as_decimal


def savings_forecast(total_income, total_expense, months_ahead: int) -> list[dict]:
    """Predice el ahorro para los próximos meses según la tendencia actual."""
    monthly_savings = as_decimal(total_income) - as_decimal(total_expense)
    if monthly_savings <= ZERO:
        return []

    results = []
    running = ZERO
    for month in range(1, months_ahead + 1):
        running += monthly_savings
        results.append(
            {
                "month": month,
                "predicted_savings": float(monthly_savings),
                "cumulative_savings": float(running),
                "confidence": max(0.90 - (month - 1) * 0.05, 0.50),
            }
        )
    return results


def goal_completion_forecast(
    current_amount, target_amount, average_monthly_savings, start_date: date | None = None
) -> dict:
    """Predice los meses y la fecha de cumplimiento de una meta."""
    months = goal_forecast_months(current_amount, target_amount, average_monthly_savings)
    forecast: dict = {"months_remaining": months}
    if months < 0:
        forecast["estimated_date"] = None
    elif months == 0:
        forecast["estimated_date"] = (start_date or date.today()).isoformat()
    else:
        base = start_date or date.today()
        year = base.year + (base.month - 1 + months) // 12
        month = (base.month - 1 + months) % 12 + 1
        day = min(base.day, 28)
        forecast["estimated_date"] = date(year, month, day).isoformat()
    return forecast


def cash_flow_forecast(total_income, total_expense, months_ahead: int) -> list[dict]:
    """Predice el flujo de caja neto para los próximos meses."""
    net = as_decimal(total_income) - as_decimal(total_expense)
    return [
        {
            "month": month,
            "predicted_net_cash_flow": float(net),
            "confidence": max(0.90 - (month - 1) * 0.05, 0.50),
        }
        for month in range(1, months_ahead + 1)
    ]


def balance_forecast(current_balance, total_income, total_expense) -> dict:
    """Predice el saldo a fin de mes."""
    monthly_net = as_decimal(total_income) - as_decimal(total_expense)
    return {
        "current_balance": float(as_decimal(current_balance)),
        "projected_month_end": float(as_decimal(current_balance) + monthly_net),
        "monthly_net_cash_flow": float(monthly_net),
    }
