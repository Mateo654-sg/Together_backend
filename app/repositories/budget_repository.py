"""
Repository de Budget (Tabla 14 — Documento 07).

Encapsula las consultas de presupuestos.
"""
import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.repositories.base_repository import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Budget)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        month: int | None = None,
        year: int | None = None,
        category_id: uuid.UUID | None = None,
    ) -> tuple[list[Budget], int]:
        base_filter = [
            Budget.user_id == user_id,
            Budget.deleted_at.is_(None),
        ]

        if month is not None:
            base_filter.append(Budget.month == month)
        if year is not None:
            base_filter.append(Budget.year == year)
        if category_id is not None:
            base_filter.append(Budget.category_id == category_id)

        count_stmt = (
            select(func.count())
            .select_from(Budget)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Budget)
            .where(*base_filter)
            .order_by(Budget.year.desc(), Budget.month.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, budget_id: uuid.UUID
    ) -> Budget | None:
        stmt = select(Budget).where(
            Budget.id == budget_id,
            Budget.user_id == user_id,
            Budget.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_category_month(
        self,
        user_id: uuid.UUID,
        category_id: uuid.UUID,
        month: int,
        year: int,
    ) -> Budget | None:
        stmt = select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.month == month,
            Budget.year == year,
            Budget.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_alerts(
        self,
        user_id: uuid.UUID,
        *,
        month: int | None = None,
        year: int | None = None,
    ) -> list[dict]:
        budgets, _ = await self.list_by_user(
            user_id, page=1, limit=1000, month=month, year=year
        )

        alerts = []
        for budget in budgets:
            spent = await self._get_spent_amount(user_id, budget)
            if budget.amount <= 0:
                continue

            percentage = float(spent / budget.amount * 100)

            if percentage >= 100:
                level = "exceeded"
            elif percentage >= 90:
                level = "critical"
            elif percentage >= 80:
                level = "warning"
            else:
                continue

            alerts.append({
                "budget_id": budget.id,
                "category_id": budget.category_id,
                "amount": budget.amount,
                "spent": spent,
                "percentage": min(percentage, 100.0),
                "level": level,
                "month": budget.month,
                "year": budget.year,
            })

        return alerts

    async def _get_spent_amount(
        self, user_id: uuid.UUID, budget: Budget
    ) -> Decimal:
        from app.models.personal_expense import PersonalExpense

        base_filter = [
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        ]

        if budget.category_id is not None:
            base_filter.append(PersonalExpense.category_id == budget.category_id)

        if budget.month and budget.year:
            from sqlalchemy import extract

            base_filter.append(extract("month", PersonalExpense.expense_date) == budget.month)
            base_filter.append(extract("year", PersonalExpense.expense_date) == budget.year)

        stmt = select(
            func.coalesce(func.sum(PersonalExpense.amount), 0)
        ).where(*base_filter)

        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))
