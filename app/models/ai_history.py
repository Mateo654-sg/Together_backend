"""
Modelo AIHistory — Historial de interacciones con la IA.

Guarda preguntas, respuestas, tokens utilizados y costo.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class AIHistory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_history"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="mock", nullable=False)
    model: Mapped[str] = mapped_column(String(100), default="mock-model", nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    feedback: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1=positive, -1=negative

    # Relationships
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<AIHistory id={self.id} endpoint={self.endpoint}>"
