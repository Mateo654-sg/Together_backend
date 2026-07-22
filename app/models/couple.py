"""
Modelo Couple — Tabla 3 (Documento 07 — Diseño de Base de Datos).

Representa la relación entre dos usuarios.
Estados: pending, accepted, rejected, separated (FR-015).
"""
from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.shared_expense import SharedExpense
    from app.models.shared_income import SharedIncome


class CoupleStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SEPARATED = "separated"


class Couple(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "couples"

    partner_one_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    partner_two_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    invitation_code: Mapped[str] = mapped_column(
        String(12), nullable=False, unique=True, index=True
    )
    status: Mapped[CoupleStatus] = mapped_column(
        SAEnum(CoupleStatus, name="couple_status"),
        default=CoupleStatus.PENDING,
        nullable=False,
    )

    # Relationships
    shared_expenses: Mapped[list["SharedExpense"]] = relationship(
        back_populates="couple", cascade="all, delete-orphan"
    )
    shared_incomes: Mapped[list["SharedIncome"]] = relationship(
        back_populates="couple", cascade="all, delete-orphan"
    )
    goals: Mapped[list["Goal"]] = relationship(
        back_populates="couple", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Couple id={self.id} status={self.status}>"
