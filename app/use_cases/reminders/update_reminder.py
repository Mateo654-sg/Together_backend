"""
Use Case: UpdateReminder (FR-110).

Edita un recordatorio existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.reminder import ReminderRepeatType
from app.repositories.reminder_repository import ReminderRepository
from app.schemas.reminder import UpdateReminderRequest


class UpdateReminderUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.reminder_repository = ReminderRepository(session)

    async def execute(
        self, user_id: uuid.UUID, reminder_id: uuid.UUID, data: UpdateReminderRequest
    ):
        reminder = await self.reminder_repository.get_by_user_and_id(user_id, reminder_id)
        if reminder is None:
            raise NotFoundException("Recordatorio no encontrado.")

        if data.title is not None:
            reminder.title = data.title.strip()
        if data.description is not None:
            reminder.description = data.description
        if data.due_date is not None:
            reminder.due_date = data.due_date
        if data.repeat_type is not None:
            try:
                reminder.repeat_type = ReminderRepeatType(data.repeat_type)
            except ValueError:
                raise ValidationException(
                    f"Tipo de repetición inválido. Permitidos: {[t.value for t in ReminderRepeatType]}"
                )
        if data.amount is not None:
            reminder.amount = data.amount

        await self.session.commit()
        await self.reminder_repository.refresh(reminder)
        return reminder
