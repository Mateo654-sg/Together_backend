"""
Modelo GoalContribution — Tabla 13 (Documento 07 — Diseño de Base de Datos).

Aportes individuales a metas compartidas.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.user import User


class GoalContribution(Base, UUIDMixin):
    __tablename__ = "goal_contributions"

    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    contribution_date: Mapped[date] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    goal: Mapped["Goal"] = relationship(back_populates="contributions")
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<GoalContribution id={self.id} amount={self.amount}>"
