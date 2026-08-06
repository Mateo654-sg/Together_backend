"""
Use Case: SendMessage (FR-118).

Envía un mensaje en el chat de pareja.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException
from app.models.chat_message import ChatMessage, MessageType
from app.repositories.chat_repository import ChatMessageRepository
from app.repositories.couple_repository import CoupleRepository
from app.schemas.chat import SendMessageRequest


class SendMessageUseCase:
    """Use Case: SendMessage (FR-118).

    Envía un mensaje en el chat de pareja.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.chat_repository = ChatMessageRepository(session)

    async def execute(
        self, sender_id: uuid.UUID, data: SendMessageRequest
    ) -> ChatMessage:
        """Envía un mensaje de chat.

        Args:
            sender_id: UUID del usuario emisor.
            data: Datos del mensaje (receiver_id, content, message_type, etc.).

        Returns:
            El mensaje de chat creado.
        """
        try:
            message_type = MessageType(data.message_type)
        except ValueError:
            message_type = MessageType.TEXT

        couple = await CoupleRepository(self.session).get_active_for_user(sender_id)
        if (
            couple is None
            or data.receiver_id not in (couple.partner_one_id, couple.partner_two_id)
        ):
            raise ForbiddenException("Solo puedes enviar mensajes a tu pareja vinculada.")

        message = ChatMessage(
            sender_id=sender_id,
            receiver_id=data.receiver_id,
            message_type=message_type,
            content=data.content,
            shared_entity_id=data.shared_entity_id,
            shared_entity_type=data.shared_entity_type,
        )
        await self.chat_repository.create(message)
        await self.session.commit()
        return message
