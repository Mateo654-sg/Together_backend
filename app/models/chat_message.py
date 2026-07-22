"""
Modelo ChatMessage — Mensajes del chat de pareja.

Permite enviar mensajes, emojis y compartir información
financiera dentro de la pareja.
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


class MessageType(str, enum.Enum):
    TEXT = "text"
    EMOJI = "emoji"
    MOTIVATIONAL = "motivational"
    SHARE_GOAL = "share_goal"
    SHARE_MOVEMENT = "share_movement"


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_messages"

    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    message_type: Mapped[MessageType] = mapped_column(
        SAEnum(MessageType, name="message_type"),
        default=MessageType.TEXT,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    shared_entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    shared_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attachment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    sender: Mapped["User"] = relationship(foreign_keys=[sender_id])
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_id])

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} sender={self.sender_id} type={self.message_type}>"
