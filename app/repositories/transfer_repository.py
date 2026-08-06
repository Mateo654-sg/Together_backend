"""
Repository de Transfer (FR-021).

Consultas de transferencias con filtros y paginación.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transfer import Transfer
from app.repositories.base_repository import BaseRepository


class TransferRepository(BaseRepository[Transfer]):
    """Repository para el modelo Transfer."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Transfer)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        date_from: date | None = None,
        date_to: date | None = None,
        method: str | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
    ) -> tuple[list[Transfer], int]:
        """Lista transferencias del usuario con filtros y paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.
            date_from: Fecha de inicio del rango (inclusive).
            date_to: Fecha de fin del rango (inclusive).
            method: Filtrar por método de origen o destino.
            min_amount: Monto mínimo de la transferencia.
            max_amount: Monto máximo de la transferencia.

        Returns:
            Tupla con la lista de transferencias y el total de registros.
        """
        base_filter = [
            Transfer.user_id == user_id,
            Transfer.deleted_at.is_(None),
        ]

        if date_from is not None:
            base_filter.append(Transfer.transfer_date >= date_from)
        if date_to is not None:
            base_filter.append(Transfer.transfer_date <= date_to)
        if method is not None:
            base_filter.append(
                (Transfer.from_method == method) | (Transfer.to_method == method)
            )
        if min_amount is not None:
            base_filter.append(Transfer.amount >= min_amount)
        if max_amount is not None:
            base_filter.append(Transfer.amount <= max_amount)

        count_stmt = select(func.count()).select_from(Transfer).where(*base_filter)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Transfer)
            .where(*base_filter)
            .order_by(Transfer.transfer_date.desc(), Transfer.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, transfer_id: uuid.UUID
    ) -> Transfer | None:
        """Obtiene una transferencia verificando que pertenezca al usuario.

        Args:
            user_id: UUID del usuario propietario.
            transfer_id: UUID de la transferencia a buscar.

        Returns:
            La transferencia encontrada o None si no existe o no pertenece al usuario.
        """
        stmt = select(Transfer).where(
            Transfer.id == transfer_id,
            Transfer.user_id == user_id,
            Transfer.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
