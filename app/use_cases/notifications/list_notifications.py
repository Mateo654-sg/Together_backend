"""
Use Case: ListNotifications (FR-134).

Lista las notificaciones del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationListResponse, NotificationResponse


class ListNotificationsUseCase:
    """Use Case: ListNotifications (FR-134).

    Lista las notificaciones del usuario con paginación y conteo de no leídas.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repository = NotificationRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        unread_only: bool = False,
    ) -> NotificationListResponse:
        """Lista notificaciones del usuario.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página.
            limit: Cantidad máxima de resultados.
            unread_only: Si True, solo muestra no leídas.

        Returns:
            NotificationListResponse con notificaciones, unread_count y paginación.
        """
        notifications, total = await self.notification_repository.list_by_user(
            user_id, page=page, limit=limit, unread_only=unread_only
        )

        data = [NotificationResponse.model_validate(n) for n in notifications]
        unread_count = await self.notification_repository.get_unread_count(user_id)

        return NotificationListResponse(
            data=data,
            unread_count=unread_count,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )
