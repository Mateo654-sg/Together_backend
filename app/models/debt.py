"""
Modelo Debt — Tabla 10 (Documento 07 — Diseño de Base de Datos).

Controla cuánto debe cada integrante de la pareja.
Se genera automáticamente al crear un gasto compartido.
"""
from __future__ import annotations

import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.shared_expense import SharedExpense
    from app.models.user import User


class DebtStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Debt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "debts"

    debtor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    creditor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    shared_expense_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_expenses.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[DebtStatus] = mapped_column(
        SAEnum(DebtStatus, name="debt_status"),
        default=DebtStatus.PENDING,
        nullable=False,
    )

    # Relationships
    debtor: Mapped["User"] = relationship(foreign_keys=[debtor_id])
    creditor: Mapped["User"] = relationship(foreign_keys=[creditor_id])
    shared_expense: Mapped["SharedExpense | None"] = relationship()

    def __repr__(self) -> str:
        return f"<Debt id={self.id} amount={self.amount} status={self.status}>"
