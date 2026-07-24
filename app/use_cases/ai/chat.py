"""
Use Case: AIChat (FR-100).

Responde preguntas en lenguaje natural sobre finanzas.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import AIChatResponse
from app.services.ai.service import AIService


class AIChatUseCase:
    """Use Case: AIChat (FR-100).

    Responde preguntas en lenguaje natural sobre finanzas del usuario.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)

    async def execute(self, user_id: uuid.UUID, question: str) -> AIChatResponse:
        """Procesa una pregunta financiera con IA.

        Args:
            user_id: UUID del usuario.
            question: Pregunta en lenguaje natural.

        Returns:
            AIChatResponse con la respuesta de la IA.
        """
        result = await self.ai_service.chat(user_id, question, endpoint="chat")
        return AIChatResponse(**result)
