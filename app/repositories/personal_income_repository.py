"""
Repository de PersonalIncome (Tabla 6 — Documento 07).

Encapsula las consultas de ingresos personales.
"""
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_income import PersonalIncome
from app.repositories.base_repository import BaseRepository


class PersonalIncomeRepository(BaseRepository[PersonalIncome]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PersonalIncome)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[PersonalIncome], int]:
        base_filter = [
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        ]

        if category_id is not None:
            base_filter.append(PersonalIncome.category_id == category_id)
        if date_from is not None:
            base_filter.append(PersonalIncome.income_date >= date_from)
        if date_to is not None:
            base_filter.append(PersonalIncome.income_date <= date_to)

        count_stmt = select(func.count()).select_from(PersonalIncome).where(
            *base_filter
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(PersonalIncome)
            .where(*base_filter)
            .order_by(PersonalIncome.income_date.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, income_id: uuid.UUID
    ) -> PersonalIncome | None:
        stmt = select(PersonalIncome).where(
            PersonalIncome.id == income_id,
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_total_by_user(self, user_id: uuid.UUID) -> Decimal:
        stmt = select(
            func.coalesce(func.sum(PersonalIncome.amount), 0)
        ).where(
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))
