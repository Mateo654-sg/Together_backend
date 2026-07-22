"""
Use Case: DeleteNotification (FR-135).

Elimina (soft delete) una notificación existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.notification_repository import NotificationRepository


class DeleteNotificationUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repository = NotificationRepository(session)

    async def execute(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> None:
        notification = await self.notification_repository.get_by_user_and_id(
            user_id, notification_id
        )
        if notification is None:
            raise NotFoundException("Notificación no encontrada.")

        await self.notification_repository.soft_delete(notification)
        await self.session.commit()
