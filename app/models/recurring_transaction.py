"""
Modelo RecurringTransaction — Tabla 22 (Documento 07 — Diseño de Base de Datos).

Movimientos recurrentes automáticos (FR-033): diario, semanal, mensual y anual.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.personal_category import PersonalCategory
    from app.models.user import User


class RecurringTransaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recurring_transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personal_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # expense | income
    frequency: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # daily | weekly | monthly | annual
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    next_execution: Mapped[date] = mapped_column(Date, nullable=False)
    last_executed: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="recurring_transactions")
    category: Mapped["PersonalCategory | None"] = relationship()

    def __repr__(self) -> str:
        return f"<RecurringTransaction id={self.id} frequency={self.frequency}>"
