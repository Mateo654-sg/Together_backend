"""
Modelo Session — Tabla 25 (Documento 07 — Diseño de Base de Datos).

Guarda las sesiones activas (refresh tokens) para permitir:
- Rotación de Refresh Tokens (Documento 12 — Seguridad).
- Cerrar sesión de dispositivos remotos.
- Historial de sesiones.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Session(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    refresh_token_jti: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    device: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="sessions")
