"""
Use Case: ListRecurringTransactions (FR-033-List).

Lista movimientos recurrentes del usuario con paginación y filtro por estado.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.recurring_transaction_repository import RecurringTransactionRepository
from app.schemas.recurring_transaction import (
    RecurringTransactionListResponse,
    RecurringTransactionResponse,
)


class ListRecurringTransactionsUseCase:
    """Use Case: ListRecurringTransactions (FR-033-List)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RecurringTransactionRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        active: bool | None = None,
    ) -> RecurringTransactionListResponse:
        """Lista movimientos recurrentes con paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página.
            limit: Cantidad máxima de resultados.
            active: Filtrar por estado activo/inactivo.

        Returns:
            RecurringTransactionListResponse con las recurrencias y paginación.
        """
        items, total = await self.repository.list_by_user(
            user_id, page=page, limit=limit, active=active
        )
        return RecurringTransactionListResponse(
            data=[RecurringTransactionResponse.model_validate(item) for item in items],
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )
