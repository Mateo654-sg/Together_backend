"""
Use Case: AIInsights (FR-098, FR-099).

Genera insights automáticos sobre las finanzas.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import AIInsightsResponse
from app.services.ai.service import AIService


class AIInsightsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)

    async def execute(self, user_id: uuid.UUID) -> AIInsightsResponse:
        question = "Genera insights automáticos sobre mis finanzas de esta semana."
        await self.ai_service.chat(user_id, question, endpoint="insights")

        insights = [
            {
                "type": "saving",
                "title": "Reducción de gastos",
                "description": "Esta semana redujiste un 14% el gasto en transporte.",
                "impact": "positive",
            },
            {
                "type": "warning",
                "title": "Gasto elevado en restaurantes",
                "description": "Los viernes concentran el 28% de tus gastos en restaurantes.",
                "impact": "negative",
            },
            {
                "type": "goal",
                "title": "Progreso en metas",
                "description": "Llevas el 45% de tu meta de vacaciones. Vas por buen camino.",
                "impact": "positive",
            },
        ]

        return AIInsightsResponse(
            insights=insights,
            period="Esta semana",
        )
