"""
Modelo LoginHistory — Tabla 26 (Documento 07 — Diseño de Base de Datos).

Historial de inicio de sesión, usado para auditoría de seguridad
(Documento 12 — Seguridad: "Registrar: Inicio de sesión, Intentos fallidos").
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class LoginHistory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "login_history"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    email_attempted: Mapped[str] = mapped_column(String(255), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    device: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
