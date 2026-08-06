"""
Repository de Export (Tabla 38 — Documento 07).

Consultas del historial de exportaciones.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export_record import Export
from app.repositories.base_repository import BaseRepository


class ExportRepository(BaseRepository[Export]):
    """Repository para el modelo Export."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Export)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Export], int]:
        """Lista el historial de exportaciones del usuario con paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.

        Returns:
            Tupla con la lista de exportaciones y el total de registros.
        """
        base_filter = [
            Export.user_id == user_id,
            Export.deleted_at.is_(None),
        ]

        count_stmt = select(func.count()).select_from(Export).where(*base_filter)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Export)
            .where(*base_filter)
            .order_by(Export.generated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total
