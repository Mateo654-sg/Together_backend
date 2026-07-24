"""
Use Case: CompleteReminder.

Marca un recordatorio como completado.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.reminder_repository import ReminderRepository
from app.schemas.reminder import ReminderResponse


class CompleteReminderUseCase:
    """Use Case: CompleteReminder.

    Alterna el estado de completado de un recordatorio (toggle).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.reminder_repository = ReminderRepository(session)

    async def execute(
        self, user_id: uuid.UUID, reminder_id: uuid.UUID
    ) -> ReminderResponse:
        """Alterna el estado completado de un recordatorio.

        Args:
            user_id: UUID del usuario propietario.
            reminder_id: UUID del recordatorio a alternar.

        Returns:
            El recordatorio con el estado actualizado.

        Raises:
            NotFoundException: Si el recordatorio no existe.
        """
        reminder = await self.reminder_repository.get_by_user_and_id(
            user_id, reminder_id
        )
        if reminder is None:
            raise NotFoundException("Recordatorio no encontrado.")

        reminder.is_completed = not reminder.is_completed
        await self.session.commit()
        await self.reminder_repository.refresh(reminder)
        return ReminderResponse.model_validate(reminder)
