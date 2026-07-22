"""
Schemas Pydantic del módulo de Notificaciones (FR-132 a FR-135).

Incluye schemas para notificaciones.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ─── Notifications ─────────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    link: str | None = None
    created_at: datetime
    updated_at: datetime


class NotificationListResponse(BaseModel):
    data: list[NotificationResponse]
    unread_count: int
    pagination: dict


class MarkReadResponse(BaseModel):
    success: bool
    message: str
    updated_count: int
