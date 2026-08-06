"""
Programación de fechas para movimientos recurrentes (FR-033).

Funciones puras y determinísticas para avanzar la próxima ejecución
según la frecuencia: diaria, semanal, mensual o anual.
"""

from datetime import date, timedelta

from app.core.exceptions import ValidationException

FREQUENCIES = ("daily", "weekly", "monthly", "annual")


def next_execution_date(frequency: str, current_date: date) -> date:
    """Calcula la siguiente fecha de ejecución.

    Args:
        frequency: daily, weekly, monthly o annual.
        current_date: Fecha base (última ejecución).

    Returns:
        La próxima fecha de ejecución.

    Raises:
        ValidationException: Si la frecuencia no es válida.
    """
    if frequency == "daily":
        return current_date + timedelta(days=1)
    if frequency == "weekly":
        return current_date + timedelta(weeks=1)
    if frequency == "monthly":
        year = current_date.year + (current_date.month - 1 + 1) // 12
        month = (current_date.month - 1 + 1) % 12 + 1
        return _safe_date(year, month, current_date.day)
    if frequency == "annual":
        return _safe_date(current_date.year + 1, current_date.month, current_date.day)
    raise ValidationException("Frecuencia no válida.")


def _safe_date(year: int, month: int, day: int) -> date:
    """Crea una fecha evitando días inválidos (ej. 31 de febrero)."""
    last_day = _days_in_month(year, month)
    return date(year, month, min(day, last_day))


def _days_in_month(year: int, month: int) -> int:
    import calendar

    return calendar.monthrange(year, month)[1]
