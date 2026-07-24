"""
Use Case: DeleteReminder (FR-111).

Elimina (soft delete) un recordatorio existente.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.reminder_repository import ReminderRepository


class DeleteReminderUseCase:
    """Use Case: DeleteReminder (FR-111).

    Elimina (soft delete) un recordatorio existente.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.reminder_repository = ReminderRepository(session)

    async def execute(self, user_id: uuid.UUID, reminder_id: uuid.UUID) -> None:
        """Elimina lógicamente un recordatorio.

        Args:
            user_id: UUID del usuario propietario.
            reminder_id: UUID del recordatorio a eliminar.

        Raises:
            NotFoundException: Si el recordatorio no existe.
        """
        reminder = await self.reminder_repository.get_by_user_and_id(
            user_id, reminder_id
        )
        if reminder is None:
            raise NotFoundException("Recordatorio no encontrado.")

        await self.reminder_repository.soft_delete(reminder)
        await self.session.commit()
