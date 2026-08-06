"""
Motor 1 y 2: Balance Personal y Balance Compartido.

Balance = Ingresos - Gastos.
"""

from decimal import Decimal

from app.financial_engine.utils import as_decimal


def personal_balance(total_income, total_expense) -> Decimal:
    """Calcula el saldo personal (ingresos - gastos)."""
    return as_decimal(total_income) - as_decimal(total_expense)


def shared_balance(total_contributions, total_shared_expenses) -> Decimal:
    """Calcula el saldo compartido (aportes totales - gastos compartidos)."""
    return as_decimal(total_contributions) - as_decimal(total_shared_expenses)
