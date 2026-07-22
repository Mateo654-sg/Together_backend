"""
Modelo Notification — Notificaciones de la aplicación.

Notificaciones push, email e in-app para el usuario.
"""
from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, enum.Enum):
    PUSH = "push"
    EMAIL = "email"
    IN_APP = "in_app"


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType, name="notification_type"),
        default=NotificationType.IN_APP,
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<Notification id={self.id} title={self.title} read={self.is_read}>"
