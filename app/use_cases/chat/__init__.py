"""
Use Case: ListChatMessages (FR-118-List).

Lista los mensajes del chat entre dos usuarios de la pareja.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chat_repository import ChatMessageRepository
from app.schemas.chat import ChatMessageListResponse, ChatMessageResponse


class ListChatMessagesUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chat_repository = ChatMessageRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        partner_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 50,
    ) -> ChatMessageListResponse:
        messages, total = await self.chat_repository.list_between_users(
            user_id, partner_id, page=page, limit=limit
        )

        data = [ChatMessageResponse.model_validate(m) for m in messages]

        return ChatMessageListResponse(
            data=data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )
