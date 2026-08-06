"""
Modelo Transfer (FR-021).

Registra el movimiento de dinero entre las propias cuentas/métodos de
pago del usuario (Efectivo, Nequi, Bancolombia, etc.). No afecta el
saldo personal total: solo reasigna el dinero entre métodos.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class Transfer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transfers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    from_method: Mapped[str] = mapped_column(String(50), nullable=False)
    to_method: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transfer_date: Mapped[date] = mapped_column(Date, nullable=False)

    def __repr__(self) -> str:
        return f"<Transfer id={self.id} amount={self.amount}>"
