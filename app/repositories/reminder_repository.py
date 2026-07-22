"""
Repository de Reminder.

Encapsula las consultas de recordatorios.
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder
from app.repositories.base_repository import BaseRepository


class ReminderRepository(BaseRepository[Reminder]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Reminder)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        completed: bool | None = None,
    ) -> tuple[list[Reminder], int]:
        base_filter = [
            Reminder.user_id == user_id,
            Reminder.deleted_at.is_(None),
        ]

        if completed is not None:
            base_filter.append(Reminder.is_completed == completed)

        count_stmt = (
            select(func.count())
            .select_from(Reminder)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Reminder)
            .where(*base_filter)
            .order_by(Reminder.due_date.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, reminder_id: uuid.UUID
    ) -> Reminder | None:
        stmt = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id,
            Reminder.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
