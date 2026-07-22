"""
Modelo SharedExpense — Tabla 8 (Documento 07 — Diseño de Base de Datos).

Gastos compartidos entre pareja con soporte para división automática.
"""
from __future__ import annotations

import enum
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.couple import Couple
    from app.models.shared_category import SharedCategory
    from app.models.user import User


class SplitType(str, enum.Enum):
    EQUAL = "equal"          # 50/50
    PERCENTAGE = "percentage"  # Por porcentaje
    CUSTOM = "custom"        # Monto personalizado


class SharedExpense(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "shared_expenses"

    couple_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("couples.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    paid_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    split_type: Mapped[SplitType] = mapped_column(
        SAEnum(SplitType, name="split_type"),
        default=SplitType.EQUAL,
        nullable=False,
    )
    split_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    attachment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    couple: Mapped["Couple"] = relationship()
    category: Mapped["SharedCategory | None"] = relationship()
    payer: Mapped["User"] = relationship(foreign_keys=[paid_by])

    def __repr__(self) -> str:
        return f"<SharedExpense id={self.id} amount={self.amount}>"
