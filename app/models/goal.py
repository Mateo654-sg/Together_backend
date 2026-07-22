"""
Modelo Goal — Tabla 12 (Documento 07 — Diseño de Base de Datos).

Metas compartidas de la pareja.
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
    from app.models.goal_contribution import GoalContribution


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Goal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "goals"

    couple_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("couples.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[GoalStatus] = mapped_column(
        SAEnum(GoalStatus, name="goal_status"),
        default=GoalStatus.ACTIVE,
        nullable=False,
    )

    # Relationships
    couple: Mapped["Couple"] = relationship()
    contributions: Mapped[list["GoalContribution"]] = relationship(
        back_populates="goal"
    )

    def __repr__(self) -> str:
        return f"<Goal id={self.id} title={self.title} status={self.status}>"
