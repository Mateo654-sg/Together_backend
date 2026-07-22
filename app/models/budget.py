"""
Modelo Budget — Tabla 14 (Documento 07 — Diseño de Base de Datos).

Presupuestos mensuales o anuales por categoría.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.personal_category import PersonalCategory
    from app.models.user import User


class Budget(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "budgets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personal_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship()
    category: Mapped["PersonalCategory | None"] = relationship()

    def __repr__(self) -> str:
        return f"<Budget id={self.id} amount={self.amount} month={self.month}/{self.year}>"
