"""
Repository de Notification.

Encapsula las consultas de notificaciones.
"""
import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Notification)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        base_filter = [
            Notification.user_id == user_id,
            Notification.deleted_at.is_(None),
        ]

        if unread_only:
            base_filter.append(~Notification.is_read)

        count_stmt = (
            select(func.count())
            .select_from(Notification)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Notification)
            .where(*base_filter)
            .order_by(Notification.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, notification_id: uuid.UUID
    ) -> Notification | None:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                ~Notification.is_read,
                Notification.deleted_at.is_(None),
            )
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            ~Notification.is_read,
            Notification.deleted_at.is_(None),
        )
        return (await self.session.execute(stmt)).scalar_one()
