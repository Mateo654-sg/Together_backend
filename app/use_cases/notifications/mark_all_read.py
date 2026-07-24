"""
Use Case: MarkAllNotificationsRead (FR-134).

Marca todas las notificaciones como leídas.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import MarkReadResponse


class MarkAllNotificationsReadUseCase:
    """Use Case: MarkAllNotificationsRead (FR-134).

    Marca todas las notificaciones del usuario como leídas.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repository = NotificationRepository(session)

    async def execute(self, user_id: uuid.UUID) -> MarkReadResponse:
        """Marca todas las notificaciones no leídas como leídas.

        Args:
            user_id: UUID del usuario.

        Returns:
            MarkReadResponse con el conteo de notificaciones actualizadas.
        """
        updated_count = await self.notification_repository.mark_all_as_read(user_id)
        await self.session.commit()

        return MarkReadResponse(
            success=True,
            message=f"{updated_count} notificaciones marcadas como leídas",
            updated_count=updated_count,
        )
