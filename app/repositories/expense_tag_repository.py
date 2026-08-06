"""
Repository de ExpenseTag (Tabla 34 — Documento 07).

Consultas de etiquetas de gastos con paginación (FR-026).
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense_tag import ExpenseTag
from app.repositories.base_repository import BaseRepository


class ExpenseTagRepository(BaseRepository[ExpenseTag]):
    """Repository para el modelo ExpenseTag."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ExpenseTag)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ExpenseTag], int]:
        """Lista las etiquetas del usuario con paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.

        Returns:
            Tupla con la lista de etiquetas y el total de registros.
        """
        base_filter = [
            ExpenseTag.user_id == user_id,
            ExpenseTag.deleted_at.is_(None),
        ]

        count_stmt = select(func.count()).select_from(ExpenseTag).where(*base_filter)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(ExpenseTag)
            .where(*base_filter)
            .order_by(ExpenseTag.name.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, tag_id: uuid.UUID
    ) -> ExpenseTag | None:
        """Obtiene una etiqueta verificando que pertenezca al usuario.

        Args:
            user_id: UUID del usuario propietario.
            tag_id: UUID de la etiqueta a buscar.

        Returns:
            La etiqueta encontrada o None si no existe o no pertenece al usuario.
        """
        stmt = select(ExpenseTag).where(
            ExpenseTag.id == tag_id,
            ExpenseTag.user_id == user_id,
            ExpenseTag.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
