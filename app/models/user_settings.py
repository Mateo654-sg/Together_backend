"""
Modelo UserSettings — Tabla 2 (Documento 07 — Diseño de Base de Datos).

Configuraciones personales del usuario.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserSettings(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    theme: Mapped[str] = mapped_column(String(10), default="dark", nullable=False)
    biometric_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_home_screen: Mapped[str] = mapped_column(
        String(30), default="dashboard", nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="settings")
