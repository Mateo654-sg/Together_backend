"""
Use Case: ListReminders (FR-109-List).

Lista los recordatorios del usuario.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.reminder_repository import ReminderRepository
from app.schemas.reminder import ReminderListResponse, ReminderResponse


class ListRemindersUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.reminder_repository = ReminderRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        completed: bool | None = None,
    ) -> ReminderListResponse:
        reminders, total = await self.reminder_repository.list_by_user(
            user_id, page=page, limit=limit, completed=completed
        )

        data = [ReminderResponse.model_validate(r) for r in reminders]

        return ReminderListResponse(
            data=data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )
