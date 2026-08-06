"""
Use Case: AIAnalyze (FR-098, FR-099, FR-107).

Detecta patrones, gastos anómalos y compara períodos.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import AIAnalyzeRequest, AIAnalyzeResponse
from app.services.ai.service import AIService


class AIAnalyzeUseCase:
    """Use Case: AIAnalyze (FR-098, FR-099, FR-107).

    Detecta patrones, gastos anómalos y compara períodos
    utilizando el servicio de IA financiera.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)

    async def execute(
        self, user_id: uuid.UUID, data: AIAnalyzeRequest
    ) -> AIAnalyzeResponse:
        prompts = {
            "patterns": "Analiza mis patrones de gasto del último mes. ¿Qué categorías dominan? ¿Hay gastos repetitivos? Dame 3 insights específicos basados en mis datos.",
            "anomalies": "Detecta gastos anómalos o inusuales en mis registros recientes. Dame 3 insights específicos.",
            "comparison": "Compara mis gastos del mes actual con el mes anterior. Dame 3 diferencias clave.",
            "categories": "Analiza la distribución de mis gastos por categoría. Dame 3 insights sobre mis patrones de gasto.",
        }

        question = prompts.get(
            data.analysis_type, f"Analiza mis finanzas: {data.analysis_type}. Dame 3 insights específicos."
        )
        result = await self.ai_service.chat(user_id, question, endpoint="analyze")

        lines = [line.strip("- ").strip() for line in result["answer"].split("\n") if line.strip()]
        insights = [line for line in lines if len(line) > 10][:5]
        if not insights:
            insights = ["Análisis completado. Revisa los detalles en el reporte."]

        return AIAnalyzeResponse(
            analysis_type=data.analysis_type,
            result={"analysis": result["answer"]},
            insights=insights,
        )
