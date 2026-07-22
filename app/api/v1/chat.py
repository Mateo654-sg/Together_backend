"""
Router: /api/v1/chat

Chat de pareja (FR-118 a FR-122).
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageListResponse,
    ChatMessageResponse,
    SendMessageRequest,
)
from app.use_cases.chat.delete_message import DeleteChatMessageUseCase
from app.use_cases.chat.list_messages import ListChatMessagesUseCase
from app.use_cases.chat.send_message import SendMessageUseCase

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("", response_model=ChatMessageListResponse)
async def list_messages(
    partner_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """FR-118: Lista mensajes del chat con la pareja."""
    use_case = ListChatMessagesUseCase(db)
    return await use_case.execute(current_user.id, partner_id, page=page, limit=limit)


@router.post("", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-118: Envía un mensaje al chat."""
    use_case = SendMessageUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-118: Elimina un mensaje del chat."""
    use_case = DeleteChatMessageUseCase(db)
    await use_case.execute(current_user.id, message_id)
