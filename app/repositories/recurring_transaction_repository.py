"""
Repository de RecurringTransaction (Tabla 22 — Documento 07).

Encapsula las consultas de movimientos recurrentes (FR-033).
"""

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring_transaction import RecurringTransaction
from app.repositories.base_repository import BaseRepository


class RecurringTransactionRepository(BaseRepository[RecurringTransaction]):
    """Repository para el modelo RecurringTransaction (FR-033)."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RecurringTransaction)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        active: bool | None = None,
    ) -> tuple[list[RecurringTransaction], int]:
        """Lista movimientos recurrentes del usuario con paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.
            active: Filtrar por estado activo/inactivo.

        Returns:
            Tupla con la lista de recurrencias y el total de registros.
        """
        base_filter = [
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.deleted_at.is_(None),
        ]
        if active is not None:
            base_filter.append(RecurringTransaction.active == active)

        count_stmt = (
            select(func.count())
            .select_from(RecurringTransaction)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(RecurringTransaction)
            .where(*base_filter)
            .order_by(RecurringTransaction.next_execution.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, recurring_id: uuid.UUID
    ) -> RecurringTransaction | None:
        """Obtiene una recurrencia verificando que pertenezca al usuario."""
        stmt = select(RecurringTransaction).where(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_due(self, user_id: uuid.UUID, on_date: date) -> list[RecurringTransaction]:
        """Lista recurrencias activas cuya próxima ejecución venció o es hoy."""
        stmt = select(RecurringTransaction).where(
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.active.is_(True),
            RecurringTransaction.deleted_at.is_(None),
            RecurringTransaction.next_execution <= on_date,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
