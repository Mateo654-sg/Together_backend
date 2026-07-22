"""
Modelo PersonalExpense — Tabla 5 (Documento 07 — Diseño de Base de Datos).

Todos los gastos privados de un usuario.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.personal_category import PersonalCategory
    from app.models.user import User


class PersonalExpense(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "personal_expenses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personal_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attachment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="personal_expenses")
    category: Mapped["PersonalCategory | None"] = relationship()

    def __repr__(self) -> str:
        return f"<PersonalExpense id={self.id} amount={self.amount}>"
