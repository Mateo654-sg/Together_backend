"""
Motor 9 y 10: Goal Progress y Goal Forecast.

Progreso = Monto Actual / Meta * 100.
Forecast = Meta / Ahorro Promedio Mensual (meses) y fecha estimada.
"""

from datetime import date, timedelta
from decimal import Decimal

from app.financial_engine.utils import ZERO, as_decimal, clamp, safe_percentage


def goal_progress(current_amount, target_amount) -> Decimal:
    """Calcula el progreso de una meta (0-100)."""
    return safe_percentage(as_decimal(current_amount), as_decimal(target_amount))


def goal_forecast_months(current_amount, target_amount, average_monthly_savings) -> int:
    """Estima los meses restantes para cumplir la meta."""
    remaining = as_decimal(target_amount) - as_decimal(current_amount)
    if remaining <= ZERO:
        return 0
    monthly = as_decimal(average_monthly_savings)
    if monthly <= ZERO:
        return -1
    import math

    return math.ceil(remaining / monthly)


def goal_forecast_date(
    current_amount, target_amount, average_monthly_savings, start_date: date | None = None
) -> date | None:
    """Estima la fecha de cumplimiento de la meta."""
    months = goal_forecast_months(current_amount, target_amount, average_monthly_savings)
    if months < 0:
        return None
    base = start_date or date.today()
    year = base.year + (base.month - 1 + months) // 12
    month = (base.month - 1 + months) % 12 + 1
    day = min(base.day, 28)
    return date(year, month, day)


def goal_on_track(
    current_amount, target_amount, target_date: date, created_date: date, today: date | None = None
) -> bool:
    """Determina si una meta va en curso de cumplimiento.

    Compara el progreso real contra el progreso esperado en el tiempo.
    """
    today = today or date.today()
    if target_date <= today:
        return as_decimal(current_amount) >= as_decimal(target_amount)

    total_days = (target_date - created_date).days
    elapsed_days = (today - created_date).days
    if total_days <= 0 or elapsed_days <= 0:
        return True

    expected = clamp(as_decimal(elapsed_days) / as_decimal(total_days), ZERO, Decimal("1"))
    actual = safe_percentage(as_decimal(current_amount), as_decimal(target_amount)) / 100
    return actual >= expected


def goal_days_remaining(target_date: date, today: date | None = None) -> int:
    """Días restantes hasta la fecha objetivo (>= 0)."""
    today = today or date.today()
    if target_date is None:
        return 0
    return max((target_date - today).days, 0)


def goal_predicted_completion(
    current_amount,
    target_amount,
    created_date: date,
    target_date: date | None,
    today: date | None = None,
) -> date | None:
    """Estima la fecha de cumplimiento según la tasa diaria de ahorro."""
    today = today or date.today()
    if as_decimal(target_amount) <= ZERO or as_decimal(current_amount) <= ZERO:
        return None
    if target_date is None:
        return None

    progress_ratio = as_decimal(current_amount) / as_decimal(target_amount)
    if progress_ratio >= 1:
        return today

    elapsed = (today - created_date).days
    if elapsed <= 0:
        return target_date

    daily_rate = as_decimal(current_amount) / elapsed
    if daily_rate <= ZERO:
        return target_date

    remaining = as_decimal(target_amount) - as_decimal(current_amount)
    import math

    return today + timedelta(days=math.ceil(remaining / daily_rate))
