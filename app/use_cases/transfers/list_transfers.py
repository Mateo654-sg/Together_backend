"""
Use Case: ListTransfers (FR-021).

Lista transferencias del usuario con filtros y paginación.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.transfer_repository import TransferRepository
from app.schemas.transfer import TransferListResponse


class ListTransfersUseCase:
    """Use Case: ListTransfers (FR-021)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TransferRepository(session)

    async def execute(
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
    ) -> TransferListResponse:
        """Lista transferencias del usuario con filtros y paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.
            date_from: Fecha de inicio del rango.
            date_to: Fecha de fin del rango.
            method: Filtrar por método de origen o destino.
            min_amount: Monto mínimo.
            max_amount: Monto máximo.

        Returns:
            TransferListResponse con las transferencias y datos de paginación.
        """
        items, total = await self.repository.list_by_user(
            user_id,
            page=page,
            limit=limit,
            date_from=date_from,
            date_to=date_to,
            method=method,
            min_amount=min_amount,
            max_amount=max_amount,
        )

        pages = max(1, -(-total // limit))

        return TransferListResponse(
            data=items,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": pages,
            },
        )
