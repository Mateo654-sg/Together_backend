"""
Modelo SharedIncome — Tabla 9 (Documento 07 — Diseño de Base de Datos).

Ingresos compartidos entre pareja.
Ejemplo: Venta conjunta, negocio.
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
    from app.models.couple import Couple
    from app.models.user import User


class SharedIncome(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "shared_incomes"

    couple_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("couples.id", ondelete="CASCADE"), nullable=False
    )
    received_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    income_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    couple: Mapped["Couple"] = relationship()
    receiver: Mapped["User"] = relationship(foreign_keys=[received_by])

    def __repr__(self) -> str:
        return f"<SharedIncome id={self.id} amount={self.amount}>"
