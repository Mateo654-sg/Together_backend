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
    """Repository para el modelo PersonalCategory.

    Encapsula las consultas de categorías personales para
    clasificar gastos e ingresos (FR-024).
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, PersonalCategory)

    async def list_by_user(self, user_id: uuid.UUID, category_type: str | None = None) -> list[PersonalCategory]:
        """Lista todas las categorías personales del usuario ordenadas alfabéticamente.

        Args:
            user_id: UUID del usuario propietario.
            category_type: Tipo de categoría a filtrar ('expense' o 'income'). None para todas.

        Returns:
            Lista de categorías activas del usuario.
        """
        filters = [
            PersonalCategory.user_id == user_id,
            PersonalCategory.deleted_at.is_(None),
        ]
        if category_type:
            filters.append(PersonalCategory.type == category_type)

        stmt = (
            select(PersonalCategory)
            .where(*filters)
            .order_by(PersonalCategory.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, category_id: uuid.UUID
    ) -> PersonalCategory | None:
        """Obtiene una categoría específica verificando que pertenezca al usuario.

        Args:
            user_id: UUID del usuario propietario.
            category_id: UUID de la categoría a buscar.

        Returns:
            La categoría encontrada o None si no existe o no pertenece al usuario.
        """
        stmt = select(PersonalCategory).where(
            PersonalCategory.id == category_id,
            PersonalCategory.user_id == user_id,
            PersonalCategory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def name_exists_for_user(self, user_id: uuid.UUID, name: str) -> bool:
        """Verifica si el usuario ya tiene una categoría con ese nombre.

        Args:
            user_id: UUID del usuario.
            name: Nombre de la categoría a verificar.

        Returns:
            True si ya existe una categoría con ese nombre, False de lo contrario.
        """
        stmt = select(PersonalCategory).where(
            PersonalCategory.user_id == user_id,
            PersonalCategory.name == name,
            PersonalCategory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
