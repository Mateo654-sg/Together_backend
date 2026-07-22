"""
Schemas Pydantic del módulo de Recordatorios (FR-109 a FR-113).

Incluye schemas para recordatorios.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ─── Reminders ─────────────────────────────────────────────────────────────────

class CreateReminderRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime
    repeat_type: str = "none"
    amount: str | None = Field(None, max_length=50)


class UpdateReminderRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    repeat_type: str | None = None
    amount: str | None = Field(None, max_length=50)


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    due_date: datetime
    repeat_type: str
    is_completed: bool
    amount: str | None
    notification_sent: bool
    created_at: datetime
    updated_at: datetime


class ReminderListResponse(BaseModel):
    data: list[ReminderResponse]
    pagination: dict
