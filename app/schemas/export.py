"""
Schemas Pydantic de exportaciones de datos financieros (FR-095 a FR-097).
"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ExportRequest(BaseModel):
    date_from: date | None = None
    date_to: date | None = None


class ExportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    format: str
    date_from: date | None
    date_to: date | None
    file_size: int
    generated_at: datetime


class ExportListResponse(BaseModel):
    data: list[ExportResponse]
    pagination: dict
