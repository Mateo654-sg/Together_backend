"""
Modelo SharedCategory — Tabla 7 (Documento 07 — Diseño de Base de Datos).

Categorías compartidas para clasificar gastos de pareja.
Ejemplo: Mercado, Viajes, Netflix, Mascotas, Arriendo, Servicios.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.couple import Couple


class SharedCategory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "shared_categories"

    couple_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("couples.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Relationships
    couple: Mapped["Couple"] = relationship()

    def __repr__(self) -> str:
        return f"<SharedCategory id={self.id} name={self.name}>"
