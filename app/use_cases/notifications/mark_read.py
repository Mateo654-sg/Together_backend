"""
Use Case: MarkNotificationRead.

Marca una notificación como leída.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationResponse


class MarkNotificationReadUseCase:
    """Use Case: MarkNotificationRead.

    Marca una notificación específica como leída.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repository = NotificationRepository(session)

    async def execute(
        self, user_id: uuid.UUID, notification_id: uuid.UUID
    ) -> NotificationResponse:
        """Marca una notificación como leída.

        Args:
            user_id: UUID del usuario propietario.
            notification_id: UUID de la notificación a marcar.

        Returns:
            La notificación actualizada.

        Raises:
            NotFoundException: Si la notificación no existe.
        """
        notification = await self.notification_repository.get_by_user_and_id(
            user_id, notification_id
        )
        if notification is None:
            raise NotFoundException("Notificación no encontrada.")

        notification.is_read = True
        await self.session.commit()
        await self.notification_repository.refresh(notification)
        return NotificationResponse.model_validate(notification)
