"""
Use Case: AISummary (FR-101, FR-102).

Genera resúmenes semanales y mensuales.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import AISummaryRequest, AISummaryResponse
from app.services.ai.service import AIService


class AISummaryUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)

    async def execute(
        self, user_id: uuid.UUID, data: AISummaryRequest, summary_type: str = "monthly"
    ) -> AISummaryResponse:
        if summary_type == "weekly":
            question = "Genera un resumen financiero de esta semana."
            period = "Semanal"
        else:
            question = "Genera un resumen financiero de este mes."
            period = "Mensual"

        result = await self.ai_service.chat(user_id, question, endpoint=f"{summary_type}-summary")

        highlights = [
            "Ingresos estables respecto al período anterior.",
            "Reducción del 8% en gastos variables.",
            "Ahorro acumulado del 32% de ingresos.",
        ]

        kpis = {
            "total_income": 2500000,
            "total_expense": 1700000,
            "savings": 800000,
            "savings_rate": 32.0,
            "transactions": 45,
        }

        return AISummaryResponse(
            period=period,
            summary=result["answer"],
            highlights=highlights,
            kpis=kpis,
        )
