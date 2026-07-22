"""
Use Case: GetUserStatistics.

Retorna estadísticas personales del usuario: total ingresos,
gastos, saldo, categorías más usadas, etc.
"""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.repositories.user_repository import UserRepository


@dataclass
class UserStatistics:
    total_income: float
    total_expenses: float
    balance: float
    total_categories_used: int
    total_expenses_count: int
    total_incomes_count: int


class GetUserStatisticsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.expense_repository = PersonalExpenseRepository(session)
        self.income_repository = PersonalIncomeRepository(session)

    async def execute(self, user_id: uuid.UUID) -> UserStatistics:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")

        balance = await self.expense_repository.get_balance(user_id)
        total_income = await self.income_repository.get_total_by_user(user_id)

        # Count expenses
        from sqlalchemy import func, select
        from app.models.personal_expense import PersonalExpense
        from app.models.personal_income import PersonalIncome

        expense_count_stmt = (
            select(func.count())
            .select_from(PersonalExpense)
            .where(
                PersonalExpense.user_id == user_id,
                PersonalExpense.deleted_at.is_(None),
            )
        )
        total_expenses_count = (
            await self.session.execute(expense_count_stmt)
        ).scalar_one()

        income_count_stmt = (
            select(func.count())
            .select_from(PersonalIncome)
            .where(
                PersonalIncome.user_id == user_id,
                PersonalIncome.deleted_at.is_(None),
            )
        )
        total_incomes_count = (
            await self.session.execute(income_count_stmt)
        ).scalar_one()

        # Count distinct categories used
        from app.models.personal_expense import PersonalExpense as PE
        from app.models.personal_income import PersonalIncome as PI

        cat_stmt = select(
            func.count(
                func.distinct(
                    func.coalesce(PE.category_id, PI.category_id)
                )
            )
        ).select_from(
            PE.__table__.outerjoin(PI.__table__, PE.user_id == PI.user_id)
        ).where(
            PE.user_id == user_id,
            PE.deleted_at.is_(None),
        )
        total_categories = (await self.session.execute(cat_stmt)).scalar_one()

        return UserStatistics(
            total_income=float(total_income),
            total_expenses=float(total_income) - float(balance),
            balance=float(balance),
            total_categories_used=total_categories or 0,
            total_expenses_count=total_expenses_count,
            total_incomes_count=total_incomes_count,
        )
