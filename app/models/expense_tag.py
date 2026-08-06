"""
Modelos para etiquetas de gastos — Tablas 34 y 35 (Documento 07).

expense_tags: etiquetas del usuario (FR-026).
expense_tag_relation: relación N:M entre gastos personales y etiquetas.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

expense_tag_relation = Table(
    "expense_tag_relation",
    Base.metadata,
    Column(
        "expense_id",
        UUID(as_uuid=True),
        ForeignKey("personal_expenses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        UUID(as_uuid=True),
        ForeignKey("expense_tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ExpenseTag(Base, UUIDMixin, TimestampMixin):
    """Etiqueta de gasto (Tabla 34 — Documento 07).

    Cada usuario puede crear etiquetas libres (Vacaciones, Trabajo,
    Casa, Urgente, etc.) y asociarlas a sus gastos personales.
    """

    __tablename__ = "expense_tags"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Relationships
    expenses = relationship(
        "PersonalExpense", secondary=expense_tag_relation, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<ExpenseTag id={self.id} name={self.name}>"
