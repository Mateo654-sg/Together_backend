"""
Use Case: AIChat (FR-100).

Responde preguntas en lenguaje natural sobre finanzas.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import AIChatResponse
from app.services.ai.service import AIService


class AIChatUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)

    async def execute(self, user_id: uuid.UUID, question: str) -> AIChatResponse:
        result = await self.ai_service.chat(user_id, question, endpoint="chat")
        return AIChatResponse(**result)
