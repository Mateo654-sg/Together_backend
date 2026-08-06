"""
Servicio: construcción de los datos financieros a exportar.

Reúne los gastos e ingresos personales del usuario en un rango de
fechas como filas normalizadas para PDF, Excel y CSV (FR-095 a FR-097).
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.personal_expense import PersonalExpense
from app.models.personal_income import PersonalIncome


class ExportDataBuilder:
    """Reúne los movimientos financieros del usuario para exportar."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def build(
        self,
        user_id: uuid.UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[dict]:
        """Retorna los movimientos como filas ordenadas por fecha.

        Args:
            user_id: UUID del usuario propietario.
            date_from: Fecha de inicio del rango (inclusive).
            date_to: Fecha de fin del rango (inclusive).

        Returns:
            Lista de dicts con keys date, type, category, description, amount.
        """
        rows: list[dict] = []

        expense_stmt = (
            select(PersonalExpense)
            .options(selectinload(PersonalExpense.category))
            .where(
                PersonalExpense.user_id == user_id,
                PersonalExpense.deleted_at.is_(None),
            )
        )
        if date_from is not None:
            expense_stmt = expense_stmt.where(PersonalExpense.expense_date >= date_from)
        if date_to is not None:
            expense_stmt = expense_stmt.where(PersonalExpense.expense_date <= date_to)

        expenses = (await self.session.execute(expense_stmt)).scalars().all()
        for expense in expenses:
            rows.append(
                {
                    "date": expense.expense_date.isoformat(),
                    "type": "Gasto",
                    "category": expense.category.name if expense.category else "",
                    "description": expense.description,
                    "amount": Decimal(str(expense.amount)),
                }
            )

        income_stmt = (
            select(PersonalIncome)
            .options(selectinload(PersonalIncome.category))
            .where(
                PersonalIncome.user_id == user_id,
                PersonalIncome.deleted_at.is_(None),
            )
        )
        if date_from is not None:
            income_stmt = income_stmt.where(PersonalIncome.income_date >= date_from)
        if date_to is not None:
            income_stmt = income_stmt.where(PersonalIncome.income_date <= date_to)

        incomes = (await self.session.execute(income_stmt)).scalars().all()
        for income in incomes:
            rows.append(
                {
                    "date": income.income_date.isoformat(),
                    "type": "Ingreso",
                    "category": income.category.name if income.category else "",
                    "description": income.description,
                    "amount": Decimal(str(income.amount)),
                }
            )

        rows.sort(key=lambda row: row["date"])
        return rows
