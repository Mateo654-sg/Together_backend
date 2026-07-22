"""
Repository de SharedCategory (Tabla 7 — Documento 07).

Categorías compartidas para clasificar gastos de pareja.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shared_category import SharedCategory
from app.repositories.base_repository import BaseRepository


class SharedCategoryRepository(BaseRepository[SharedCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SharedCategory)

    async def list_by_couple(self, couple_id: uuid.UUID) -> list[SharedCategory]:
        stmt = (
            select(SharedCategory)
            .where(
                SharedCategory.couple_id == couple_id,
                SharedCategory.deleted_at.is_(None),
            )
            .order_by(SharedCategory.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_couple_and_id(
        self, couple_id: uuid.UUID, category_id: uuid.UUID
    ) -> SharedCategory | None:
        stmt = select(SharedCategory).where(
            SharedCategory.id == category_id,
            SharedCategory.couple_id == couple_id,
            SharedCategory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def name_exists_for_couple(self, couple_id: uuid.UUID, name: str) -> bool:
        stmt = select(SharedCategory).where(
            SharedCategory.couple_id == couple_id,
            SharedCategory.name == name,
            SharedCategory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
