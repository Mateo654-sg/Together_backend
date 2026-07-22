"""
Modelo PersonalCategory — Tabla 4 (Documento 07 — Diseño de Base de Datos).

Categorías personales para clasificar gastos e ingresos.
Ejemplo: Comida, Transporte, Salud, Educación, Tecnología.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class PersonalCategory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "personal_categories"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="personal_categories")

    def __repr__(self) -> str:
        return f"<PersonalCategory id={self.id} name={self.name}>"
