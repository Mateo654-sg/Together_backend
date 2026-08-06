"""
Use Case: GetPersonalStatistics (FR-092).

Obtiene estadísticas personales del usuario.
"""

import uuid
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.financial_engine import top_categories
from app.models.personal_category import PersonalCategory
from app.models.personal_expense import PersonalExpense
from app.models.personal_income import PersonalIncome
from app.schemas.report import PersonalStatisticsResponse


class GetPersonalStatisticsUseCase:
    """Use Case: GetPersonalStatistics (FR-092).

    Obtiene estadísticas personales acumuladas del usuario.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, user_id: uuid.UUID) -> PersonalStatisticsResponse:
        """Calcula estadísticas personales acumuladas.

        Args:
            user_id: UUID del usuario.

        Returns:
            PersonalStatisticsResponse con totales, balance, tasa de ahorro,
            categorías principales y tendencia mensual.
        """
        income_stmt = select(func.coalesce(func.sum(PersonalIncome.amount), 0)).where(
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        )
        total_income = Decimal(
            str((await self.session.execute(income_stmt)).scalar_one())
        )

        expense_stmt = select(func.coalesce(func.sum(PersonalExpense.amount), 0)).where(
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        )
        total_expense = Decimal(
            str((await self.session.execute(expense_stmt)).scalar_one())
        )

        balance = total_income - total_expense
        savings_rate = float(balance / total_income * 100) if total_income > 0 else 0.0

        expense_category_stmt = (
            select(PersonalCategory.name, func.sum(PersonalExpense.amount))
            .join(PersonalExpense, PersonalExpense.category_id == PersonalCategory.id)
            .where(
                PersonalExpense.user_id == user_id,
                PersonalExpense.deleted_at.is_(None),
            )
            .group_by(PersonalCategory.name)
        )
        expense_totals = {
            name: Decimal(str(total))
            for name, total in (await self.session.execute(expense_category_stmt)).all()
        }

        income_category_stmt = (
            select(PersonalCategory.name, func.sum(PersonalIncome.amount))
            .join(PersonalIncome, PersonalIncome.category_id == PersonalCategory.id)
            .where(
                PersonalIncome.user_id == user_id,
                PersonalIncome.deleted_at.is_(None),
            )
            .group_by(PersonalCategory.name)
        )
        income_totals = {
            name: Decimal(str(total))
            for name, total in (await self.session.execute(income_category_stmt)).all()
        }

        monthly_trend = []
        trend_stmt = select(
            extract("month", PersonalExpense.expense_date),
            extract("year", PersonalExpense.expense_date),
            func.sum(PersonalExpense.amount),
        ).where(
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        ).group_by(
            extract("month", PersonalExpense.expense_date),
            extract("year", PersonalExpense.expense_date),
        ).order_by(
            extract("year", PersonalExpense.expense_date),
            extract("month", PersonalExpense.expense_date),
        )
        for month, year, amount in (await self.session.execute(trend_stmt)).all():
            monthly_trend.append(
                {
                    "month": int(month),
                    "year": int(year),
                    "expense": float(amount),
                }
            )

        return PersonalStatisticsResponse(
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            savings_rate=round(savings_rate, 2),
            top_expense_categories=top_categories(expense_totals),
            top_income_categories=top_categories(income_totals),
            monthly_trend=monthly_trend,
        )
