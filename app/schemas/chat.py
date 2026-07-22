"""
Schemas Pydantic del módulo de Chat de Pareja (FR-118 a FR-122).

Incluye schemas para mensajes del chat.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SendMessageRequest(BaseModel):
    receiver_id: uuid.UUID
    message_type: str = "text"
    content: str = Field(..., min_length=1, max_length=5000)
    shared_entity_id: uuid.UUID | None = None
    shared_entity_type: str | None = Field(None, max_length=50)


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    message_type: str
    content: str
    shared_entity_id: uuid.UUID | None
    shared_entity_type: str | None
    is_read: bool
    attachment_url: str | None
    created_at: datetime
    updated_at: datetime


class ChatMessageListResponse(BaseModel):
    data: list[ChatMessageResponse]
    pagination: dict
