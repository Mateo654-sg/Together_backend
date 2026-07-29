"""
Servicio principal de IA.

Orquesta las consultas de IA a través del AI Gateway.
"""

import time
import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_history import AIHistory
from app.repositories.ai_history_repository import AIHistoryRepository
from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.context_builder import AIContextBuilder
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai.openai_provider import OpenAIProvider


class AIService:
    """Servicio principal de IA con AI Gateway.

    Orquesta las consultas al proveedor de IA, construye contexto,
    registra historial y gestiona feedback del usuario.
    """

    def __init__(self, session: AsyncSession, provider: AIProvider | None = None):
        self.session = session
        if provider:
            self.provider = provider
        elif settings.openai_api_key:
            self.provider = OpenAIProvider(settings.openai_api_key)
        else:
            self.provider = MockAIProvider()
        self.context_builder = AIContextBuilder(session)
        self.history_repository = AIHistoryRepository(session)

    async def chat(
        self, user_id: uuid.UUID, question: str, endpoint: str = "chat"
    ) -> dict:
        """Envía una consulta al proveedor de IA y registra la interacción.

        Args:
            user_id: UUID del usuario que realiza la consulta.
            question: Pregunta o prompt del usuario.
            endpoint: Nombre del endpoint que origina la consulta.

        Returns:
            Diccionario con 'answer', 'tokens_used' y 'provider'.
        """
        context = await self.context_builder.build_context(user_id)

        start_time = time.monotonic()
        result = await self.provider.generate(question, context)
        response_time_ms = int((time.monotonic() - start_time) * 1000)

        history = AIHistory(
            user_id=user_id,
            question=question,
            answer=result["answer"],
            endpoint=endpoint,
            tokens_input=result.get("tokens_input", 0),
            tokens_output=result.get("tokens_output", 0),
            cost_usd=0.0,
            provider=self.provider.name,
            model=self.provider.model,
            response_time_ms=response_time_ms,
        )
        await self.history_repository.create(history)
        await self.session.commit()

        return {
            "answer": result["answer"],
            "tokens_used": result.get("tokens_input", 0)
            + result.get("tokens_output", 0),
            "provider": self.provider.name,
        }

    async def add_feedback(
        self, user_id: uuid.UUID, history_id: uuid.UUID, feedback: int
    ) -> None:
        history = await self.history_repository.get_by_user_and_id(user_id, history_id)
        if history:
            history.feedback = feedback
            await self.session.commit()
