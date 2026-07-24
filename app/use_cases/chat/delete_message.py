"""
Use Case: DeleteChatMessage (FR-118-Delete).

Elimina un mensaje del chat (solo el remitente puede eliminarlo).
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.chat_repository import ChatMessageRepository


class DeleteChatMessageUseCase:
    """Use Case: DeleteChatMessage (FR-118-Delete).

    Elimina un mensaje del chat (solo el remitente puede eliminarlo).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.chat_repository = ChatMessageRepository(session)

    async def execute(self, sender_id: uuid.UUID, message_id: uuid.UUID) -> None:
        """Elimina lógicamente un mensaje de chat.

        Args:
            sender_id: UUID del emisor del mensaje.
            message_id: UUID del mensaje a eliminar.

        Raises:
            NotFoundException: Si el mensaje no existe o no pertenece al emisor.
        """
        message = await self.chat_repository.get_by_sender_and_id(sender_id, message_id)
        if not message:
            raise NotFoundException("Mensaje no encontrado o no eres el remitente.")
        await self.chat_repository.soft_delete(message)
        await self.session.commit()
