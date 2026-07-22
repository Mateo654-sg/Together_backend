"""
Use Case: CreateReminder (FR-109).

Crea un nuevo recordatorio.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder, ReminderRepeatType
from app.repositories.reminder_repository import ReminderRepository
from app.schemas.reminder import CreateReminderRequest


class CreateReminderUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.reminder_repository = ReminderRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateReminderRequest
    ) -> Reminder:
        try:
            repeat_type = ReminderRepeatType(data.repeat_type)
        except ValueError:
            repeat_type = ReminderRepeatType.NONE

        reminder = Reminder(
            user_id=user_id,
            title=data.title.strip(),
            description=data.description,
            due_date=data.due_date,
            repeat_type=repeat_type,
            amount=data.amount,
        )
        await self.reminder_repository.create(reminder)
        await self.session.commit()
        await self.reminder_repository.refresh(reminder)
        return reminder
