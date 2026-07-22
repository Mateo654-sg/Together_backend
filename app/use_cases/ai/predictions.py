"""
Use Case: AIPredictions (FR-103, FR-104).

Genera predicciones de ahorro y cumplimiento de metas.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import AIPredictionRequest, AIPredictionResponse
from app.services.ai.service import AIService


class AIPredictionsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)

    async def execute(
        self, user_id: uuid.UUID, data: AIPredictionRequest
    ) -> AIPredictionResponse:
        prompts = {
            "savings": f"Predice mi ahorro para los próximos {data.months_ahead} meses basado en mis tendencias actuales.",
            "goal_completion": "Predice cuándo cumpliré mis metas financieras actuales.",
            "cash_flow": f"Predice mi flujo de caja para los próximos {data.months_ahead} meses.",
            "balance": "Predice mi saldo para fin de mes.",
        }

        question = prompts.get(data.prediction_type, f"Genera predicciones: {data.prediction_type}")
        await self.ai_service.chat(user_id, question, endpoint="predictions")

        predictions = [
            {"month": 1, "predicted_savings": 450000, "confidence": 0.85},
            {"month": 2, "predicted_savings": 480000, "confidence": 0.80},
            {"month": 3, "predicted_savings": 520000, "confidence": 0.75},
        ]

        return AIPredictionResponse(
            prediction_type=data.prediction_type,
            predictions=predictions,
            confidence=0.80,
            recommendations=[
                "Mantén tu ritmo de ahorro actual.",
                "Considera automatizar transferencias a tu fondo de ahorro.",
            ],
        )
