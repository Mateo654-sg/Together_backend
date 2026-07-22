"""
Modelo Report — Reportes generados por el usuario.

Almacena metadatos de reportes generados para descarga posterior.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class ReportType(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    CATEGORY = "category"
    PERSONAL = "personal"
    COUPLE = "couple"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reports"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    report_type: Mapped[ReportType] = mapped_column(
        SAEnum(ReportType, name="report_type"), nullable=False
    )
    format: Mapped[ReportFormat] = mapped_column(
        SAEnum(ReportFormat, name="report_format"), nullable=False
    )
    status: Mapped[ReportStatus] = mapped_column(
        SAEnum(ReportStatus, name="report_status"),
        default=ReportStatus.PENDING,
        nullable=False,
    )
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    parameters: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<Report id={self.id} type={self.report_type} status={self.status}>"
