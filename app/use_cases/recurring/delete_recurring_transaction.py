"""
Use Case: DeleteRecurringTransaction (FR-033-Delete).

Elimina (soft delete) un movimiento recurrente.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.recurring_transaction_repository import RecurringTransactionRepository


class DeleteRecurringTransactionUseCase:
    """Use Case: DeleteRecurringTransaction (FR-033-Delete)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RecurringTransactionRepository(session)

    async def execute(self, user_id: uuid.UUID, recurring_id: uuid.UUID) -> None:
        """Elimina un movimiento recurrente (soft delete).

        Args:
            user_id: UUID del usuario propietario.
            recurring_id: UUID de la recurrencia a eliminar.

        Raises:
            NotFoundException: Si la recurrencia no existe.
        """
        recurrence = await self.repository.get_by_user_and_id(user_id, recurring_id)
        if recurrence is None:
            raise NotFoundException("Movimiento recurrente no encontrado.")

        await self.repository.soft_delete(recurrence)
        await self.session.commit()
