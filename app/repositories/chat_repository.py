"""
Repository de ChatMessage.

Encapsula las consultas de mensajes del chat de pareja.
"""
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.repositories.base_repository import BaseRepository


class ChatMessageRepository(BaseRepository[ChatMessage]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChatMessage)

    async def list_between_users(
        self,
        user1_id: uuid.UUID,
        user2_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[ChatMessage], int]:
        base_filter = [
            or_(
                (ChatMessage.sender_id == user1_id) & (ChatMessage.receiver_id == user2_id),
                (ChatMessage.sender_id == user2_id) & (ChatMessage.receiver_id == user1_id),
            ),
            ChatMessage.deleted_at.is_(None),
        ]

        count_stmt = (
            select(func.count())
            .select_from(ChatMessage)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(ChatMessage)
            .where(*base_filter)
            .order_by(ChatMessage.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_sender_and_id(
        self, sender_id: uuid.UUID, message_id: uuid.UUID
    ) -> ChatMessage | None:
        stmt = select(ChatMessage).where(
            ChatMessage.id == message_id,
            ChatMessage.sender_id == sender_id,
            ChatMessage.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_as_read(self, sender_id: uuid.UUID, receiver_id: uuid.UUID) -> int:
        from sqlalchemy import update

        stmt = (
            update(ChatMessage)
            .where(
                ChatMessage.sender_id == sender_id,
                ChatMessage.receiver_id == receiver_id,
                ChatMessage.is_read == False,  # noqa: E712
                ChatMessage.deleted_at.is_(None),
            )
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(ChatMessage).where(
            ChatMessage.receiver_id == user_id,
            ChatMessage.is_read == False,  # noqa: E712
            ChatMessage.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
