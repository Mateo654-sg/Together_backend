"""
Router: /api/v1/notifications

Notificaciones de la aplicación (FR-132 a FR-135).
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import (
    MarkReadResponse,
    NotificationListResponse,
    NotificationResponse,
)
from app.use_cases.notifications.delete_notification import DeleteNotificationUseCase
from app.use_cases.notifications.list_notifications import ListNotificationsUseCase
from app.use_cases.notifications.mark_all_read import MarkAllNotificationsReadUseCase
from app.use_cases.notifications.mark_read import MarkNotificationReadUseCase

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    unread_only: bool = Query(False),
):
    """FR-134: Lista notificaciones del usuario."""
    use_case = ListNotificationsUseCase(db)
    return await use_case.execute(
        current_user.id, page=page, limit=limit, unread_only=unread_only
    )


@router.patch("/read", response_model=MarkReadResponse)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-134: Marcar todas las notificaciones como leídas."""
    use_case = MarkAllNotificationsReadUseCase(db)
    return await use_case.execute(current_user.id)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-134: Marcar una notificación como leída."""
    use_case = MarkNotificationReadUseCase(db)
    return await use_case.execute(current_user.id, notification_id)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-135: Eliminar una notificación (soft delete)."""
    use_case = DeleteNotificationUseCase(db)
    await use_case.execute(current_user.id, notification_id)
