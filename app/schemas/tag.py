"""
Schemas Pydantic de etiquetas de gastos (FR-026).
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateTagRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str | None = Field(None, max_length=7)


class UpdateTagRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    color: str | None = Field(None, max_length=7)


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    color: str | None
    created_at: datetime


class TagListResponse(BaseModel):
    data: list[TagResponse]
    pagination: dict
