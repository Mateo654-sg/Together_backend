"""
Base declarativa de SQLAlchemy y mixins comunes.

Según el Documento 07 — Diseño de Base de Datos:
- Todas las tablas usan UUID como llave primaria.
- Todas las tablas tienen created_at, updated_at, deleted_at (Soft Delete).
- Nunca se realiza DELETE físico.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""
    pass


class UUIDMixin:
    """Mixin que agrega una llave primaria UUID."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """Mixin de auditoría temporal con Soft Delete."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
