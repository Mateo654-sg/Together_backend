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
    """Repository para el modelo ChatMessage.

    Encapsula las consultas de mensajes del chat de pareja,
    incluyendo marcado como leídas y conteo de no leídos.
    """

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
        """Lista mensajes entre dos usuarios con paginación.

        Recupera mensajes donde user1 es emisor y user2 receptor, o viceversa.

        Args:
            user1_id: UUID del primer usuario.
            user2_id: UUID del segundo usuario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.

        Returns:
            Tupla con la lista de mensajes y el total de registros.
        """
        base_filter = [
            or_(
                (ChatMessage.sender_id == user1_id)
                & (ChatMessage.receiver_id == user2_id),
                (ChatMessage.sender_id == user2_id)
                & (ChatMessage.receiver_id == user1_id),
            ),
            ChatMessage.deleted_at.is_(None),
        ]

        count_stmt = select(func.count()).select_from(ChatMessage).where(*base_filter)
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
        """Obtiene un mensaje verificando que el emisor coincida.

        Args:
            sender_id: UUID del emisor del mensaje.
            message_id: UUID del mensaje a buscar.

        Returns:
            El mensaje encontrado o None si no existe o no pertenece al emisor.
        """
        stmt = select(ChatMessage).where(
            ChatMessage.id == message_id,
            ChatMessage.sender_id == sender_id,
            ChatMessage.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_as_read(self, sender_id: uuid.UUID, receiver_id: uuid.UUID) -> int:
        """Marca todos los mensajes no leídos de un emisor para un receptor como leídos.

        Args:
            sender_id: UUID del emisor de los mensajes.
            receiver_id: UUID del receptor que marca como leídos.

        Returns:
            Número de mensajes marcados como leídos.
        """
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
        """Cuenta los mensajes no leídos para un usuario.

        Args:
            user_id: UUID del usuario receptor.

        Returns:
            Cantidad de mensajes no leídos.
        """
        stmt = (
            select(func.count())
            .select_from(ChatMessage)
            .where(
                ChatMessage.receiver_id == user_id,
                ChatMessage.is_read == False,  # noqa: E712
                ChatMessage.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
