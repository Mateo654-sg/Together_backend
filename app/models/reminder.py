"""
Modelo Reminder — Recordatorios financieros.

Permite crear recordatorios de pagos, vencimientos y tareas recurrentes.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class ReminderRepeatType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Reminder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reminders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    repeat_type: Mapped[ReminderRepeatType] = mapped_column(
        SAEnum(ReminderRepeatType, name="reminder_repeat_type"),
        default=ReminderRepeatType.NONE,
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    amount: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<Reminder id={self.id} title={self.title} completed={self.is_completed}>"
