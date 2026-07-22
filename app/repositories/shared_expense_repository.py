"""
Repository de SharedExpense (Tabla 8 — Documento 07).

Encapsula las consultas de gastos compartidos con soporte para
filtros y paginación.
"""
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shared_expense import SharedExpense
from app.repositories.base_repository import BaseRepository


class SharedExpenseRepository(BaseRepository[SharedExpense]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SharedExpense)

    async def list_by_couple(
        self,
        couple_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[SharedExpense], int]:
        base_filter = [
            SharedExpense.couple_id == couple_id,
            SharedExpense.deleted_at.is_(None),
        ]

        if category_id is not None:
            base_filter.append(SharedExpense.category_id == category_id)
        if date_from is not None:
            base_filter.append(SharedExpense.expense_date >= date_from)
        if date_to is not None:
            base_filter.append(SharedExpense.expense_date <= date_to)

        count_stmt = (
            select(func.count())
            .select_from(SharedExpense)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(SharedExpense)
            .where(*base_filter)
            .order_by(SharedExpense.expense_date.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_couple_and_id(
        self, couple_id: uuid.UUID, expense_id: uuid.UUID
    ) -> SharedExpense | None:
        stmt = select(SharedExpense).where(
            SharedExpense.id == expense_id,
            SharedExpense.couple_id == couple_id,
            SharedExpense.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_total_by_couple(self, couple_id: uuid.UUID) -> Decimal:
        stmt = select(
            func.coalesce(func.sum(SharedExpense.amount), 0)
        ).where(
            SharedExpense.couple_id == couple_id,
            SharedExpense.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))

    async def get_paid_by_partner(
        self, couple_id: uuid.UUID, partner_id: uuid.UUID
    ) -> Decimal:
        stmt = select(
            func.coalesce(func.sum(SharedExpense.amount), 0)
        ).where(
            SharedExpense.couple_id == couple_id,
            SharedExpense.paid_by == partner_id,
            SharedExpense.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))
