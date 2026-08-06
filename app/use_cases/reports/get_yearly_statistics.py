"""
Use Case: GetYearlyStatistics (FR-090).

Obtiene estadísticas del año actual o un año específico.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.financial_engine import savings_rate as fre_savings_rate, top_categories
from app.models.personal_category import PersonalCategory
from app.models.personal_expense import PersonalExpense
from app.models.personal_income import PersonalIncome
from app.schemas.report import YearlyStatisticsResponse


class GetYearlyStatisticsUseCase:
    """Use Case: GetYearlyStatistics (FR-090).

    Obtiene estadísticas anuales del usuario: totales, desglose
    mensual y categorías principales.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, user_id: uuid.UUID, *, year: int | None = None) -> YearlyStatisticsResponse:
        """Calcula estadísticas anuales del usuario.

        Args:
            user_id: UUID del usuario.
            year: Año a consultar (default: año actual).

        Returns:
            YearlyStatisticsResponse con totales, desglose mensual y categorías.
        """
        target_year = year or date.today().year

        income_stmt = select(func.coalesce(func.sum(PersonalIncome.amount), 0)).where(
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
            extract("year", PersonalIncome.income_date) == target_year,
        )
        total_income = Decimal(str((await self.session.execute(income_stmt)).scalar_one()))

        expense_stmt = select(func.coalesce(func.sum(PersonalExpense.amount), 0)).where(
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
            extract("year", PersonalExpense.expense_date) == target_year,
        )
        total_expense = Decimal(str((await self.session.execute(expense_stmt)).scalar_one()))

        balance = total_income - total_expense
        savings_rate = float(fre_savings_rate(total_income, total_expense))

        monthly_breakdown = []
        for month in range(1, 13):
            month_income = select(func.coalesce(func.sum(PersonalIncome.amount), 0)).where(
                PersonalIncome.user_id == user_id,
                PersonalIncome.deleted_at.is_(None),
                extract("year", PersonalIncome.income_date) == target_year,
                extract("month", PersonalIncome.income_date) == month,
            )
            month_expense = select(func.coalesce(func.sum(PersonalExpense.amount), 0)).where(
                PersonalExpense.user_id == user_id,
                PersonalExpense.deleted_at.is_(None),
                extract("year", PersonalExpense.expense_date) == target_year,
                extract("month", PersonalExpense.expense_date) == month,
            )
            income = Decimal(str((await self.session.execute(month_income)).scalar_one()))
            expense = Decimal(str((await self.session.execute(month_expense)).scalar_one()))
            monthly_breakdown.append(
                {
                    "month": month,
                    "income": float(income),
                    "expense": float(expense),
                    "balance": float(income - expense),
                }
            )

        category_totals = await self._expense_totals_by_category(user_id, target_year)

        return YearlyStatisticsResponse(
            year=target_year,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            savings_rate=round(savings_rate, 2),
            monthly_breakdown=monthly_breakdown,
            top_categories=top_categories(category_totals),
        )

    async def _expense_totals_by_category(
        self, user_id: uuid.UUID, year: int
    ) -> dict[str, Decimal]:
        """Retorna el total de gastos por nombre de categoría en el año."""
        stmt = (
            select(PersonalCategory.name, func.sum(PersonalExpense.amount))
            .join(PersonalExpense, PersonalExpense.category_id == PersonalCategory.id)
            .where(
                PersonalExpense.user_id == user_id,
                PersonalExpense.deleted_at.is_(None),
                extract("year", PersonalExpense.expense_date) == year,
            )
            .group_by(PersonalCategory.name)
        )
        result = await self.session.execute(stmt)
        return {name: Decimal(str(total)) for name, total in result.all()}
