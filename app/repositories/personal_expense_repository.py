"""
Repository de PersonalExpense (Tabla 5 — Documento 07).

Encapsula las consultas de gastos personales con soporte para
filtros, búsqueda y paginación (FR-036, FR-037, FR-038).
"""
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_expense import PersonalExpense
from app.repositories.base_repository import BaseRepository


class PersonalExpenseRepository(BaseRepository[PersonalExpense]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PersonalExpense)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        search: str | None = None,
        sort_by: str = "expense_date",
        sort_order: str = "desc",
    ) -> tuple[list[PersonalExpense], int]:
        base_filter = [
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        ]

        if category_id is not None:
            base_filter.append(PersonalExpense.category_id == category_id)
        if date_from is not None:
            base_filter.append(PersonalExpense.expense_date >= date_from)
        if date_to is not None:
            base_filter.append(PersonalExpense.expense_date <= date_to)
        if min_amount is not None:
            base_filter.append(PersonalExpense.amount >= min_amount)
        if max_amount is not None:
            base_filter.append(PersonalExpense.amount <= max_amount)
        if search:
            base_filter.append(
                PersonalExpense.description.ilike(f"%{search}%")
            )

        # Count
        count_stmt = select(func.count()).select_from(PersonalExpense).where(
            *base_filter
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        # Sort
        sort_column = getattr(PersonalExpense, sort_by, PersonalExpense.expense_date)
        if sort_order == "asc":
            order = sort_column.asc()
        else:
            order = sort_column.desc()

        # Paginate
        stmt = (
            select(PersonalExpense)
            .where(*base_filter)
            .order_by(order)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, expense_id: uuid.UUID
    ) -> PersonalExpense | None:
        stmt = select(PersonalExpense).where(
            PersonalExpense.id == expense_id,
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_balance(self, user_id: uuid.UUID) -> Decimal:
        """FR-040: Consultar saldo personal (ingresos - gastos)."""
        from app.models.personal_income import PersonalIncome

        income_stmt = select(
            func.coalesce(func.sum(PersonalIncome.amount), 0)
        ).where(
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        )
        total_income = (await self.session.execute(income_stmt)).scalar_one()

        expense_stmt = select(
            func.coalesce(func.sum(PersonalExpense.amount), 0)
        ).where(
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        )
        total_expense = (await self.session.execute(expense_stmt)).scalar_one()

        return Decimal(str(total_income)) - Decimal(str(total_expense))
