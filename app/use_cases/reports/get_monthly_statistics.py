"""
Use Case: GetMonthlyStatistics (FR-089).

Obtiene estadísticas del mes actual o un mes específico.
"""
import uuid
from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_expense import PersonalExpense
from app.models.personal_income import PersonalIncome
from app.schemas.report import MonthlyStatisticsResponse


class GetMonthlyStatisticsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        month: int | None = None,
        year: int | None = None,
    ) -> MonthlyStatisticsResponse:
        today = date.today()
        target_month = month or today.month
        target_year = year or today.year

        income_stmt = select(
            func.coalesce(func.sum(PersonalIncome.amount), 0)
        ).where(
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
            extract("month", PersonalIncome.income_date) == target_month,
            extract("year", PersonalIncome.income_date) == target_year,
        )
        total_income = Decimal(str((await self.session.execute(income_stmt)).scalar_one()))

        expense_stmt = select(
            func.coalesce(func.sum(PersonalExpense.amount), 0)
        ).where(
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
            extract("month", PersonalExpense.expense_date) == target_month,
            extract("year", PersonalExpense.expense_date) == target_year,
        )
        total_expense = Decimal(str((await self.session.execute(expense_stmt)).scalar_one()))

        balance = total_income - total_expense
        savings_rate = float(balance / total_income * 100) if total_income > 0 else 0.0

        days_in_month = monthrange(target_year, target_month)[1]
        daily_average = total_expense / days_in_month if days_in_month > 0 else Decimal("0")

        return MonthlyStatisticsResponse(
            month=target_month,
            year=target_year,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            savings_rate=round(savings_rate, 2),
            top_categories=[],
            daily_average_expense=daily_average,
        )
