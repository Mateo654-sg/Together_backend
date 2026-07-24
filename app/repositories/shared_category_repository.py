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
    """Repository para el modelo SharedCategory.

    Categorías compartidas para clasificar gastos de pareja
    (ej: Mercado, Viajes, Netflix, Mascotas, Arriendo, Servicios).
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, SharedCategory)

    async def list_by_couple(self, couple_id: uuid.UUID) -> list[SharedCategory]:
        """Lista todas las categorías compartidas de la pareja ordenadas alfabéticamente.

        Args:
            couple_id: UUID de la pareja.

        Returns:
            Lista de categorías activas de la pareja.
        """
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
        """Obtiene una categoría compartida verificando que pertenezca a la pareja.

        Args:
            couple_id: UUID de la pareja.
            category_id: UUID de la categoría a buscar.

        Returns:
            La categoría encontrada o None si no existe o no pertenece a la pareja.
        """
        stmt = select(SharedCategory).where(
            SharedCategory.id == category_id,
            SharedCategory.couple_id == couple_id,
            SharedCategory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def name_exists_for_couple(self, couple_id: uuid.UUID, name: str) -> bool:
        """Verifica si la pareja ya tiene una categoría con ese nombre.

        Args:
            couple_id: UUID de la pareja.
            name: Nombre de la categoría a verificar.

        Returns:
            True si ya existe una categoría con ese nombre, False de lo contrario.
        """
        stmt = select(SharedCategory).where(
            SharedCategory.couple_id == couple_id,
            SharedCategory.name == name,
            SharedCategory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
