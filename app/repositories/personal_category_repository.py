"""
Repository de PersonalCategory (Tabla 4 — Documento 07).

Encapsula las consultas de categorías personales.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_category import PersonalCategory
from app.repositories.base_repository import BaseRepository


class PersonalCategoryRepository(BaseRepository[PersonalCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PersonalCategory)

    async def list_by_user(self, user_id: uuid.UUID) -> list[PersonalCategory]:
        stmt = (
            select(PersonalCategory)
            .where(
                PersonalCategory.user_id == user_id,
                PersonalCategory.deleted_at.is_(None),
            )
            .order_by(PersonalCategory.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, category_id: uuid.UUID
    ) -> PersonalCategory | None:
        stmt = select(PersonalCategory).where(
            PersonalCategory.id == category_id,
            PersonalCategory.user_id == user_id,
            PersonalCategory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def name_exists_for_user(self, user_id: uuid.UUID, name: str) -> bool:
        stmt = select(PersonalCategory).where(
            PersonalCategory.user_id == user_id,
            PersonalCategory.name == name,
            PersonalCategory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
