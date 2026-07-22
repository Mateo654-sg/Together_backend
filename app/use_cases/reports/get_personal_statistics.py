"""
Use Case: GetPersonalStatistics (FR-092).

Obtiene estadísticas personales del usuario.
"""
import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_expense import PersonalExpense
from app.models.personal_income import PersonalIncome
from app.schemas.report import PersonalStatisticsResponse


class GetPersonalStatisticsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, user_id: uuid.UUID) -> PersonalStatisticsResponse:
        income_stmt = select(
            func.coalesce(func.sum(PersonalIncome.amount), 0)
        ).where(
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        )
        total_income = Decimal(str((await self.session.execute(income_stmt)).scalar_one()))

        expense_stmt = select(
            func.coalesce(func.sum(PersonalExpense.amount), 0)
        ).where(
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        )
        total_expense = Decimal(str((await self.session.execute(expense_stmt)).scalar_one()))

        balance = total_income - total_expense
        savings_rate = float(balance / total_income * 100) if total_income > 0 else 0.0

        return PersonalStatisticsResponse(
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            savings_rate=round(savings_rate, 2),
            top_expense_categories=[],
            top_income_categories=[],
            monthly_trend=[],
        )
