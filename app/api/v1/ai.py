"""
Router: /api/v1/ai

Asistente Financiero Inteligente (FR-098 a FR-108).
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.ai_history_repository import AIHistoryRepository
from app.schemas.ai import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    AIChatRequest,
    AIChatResponse,
    AIFeedbackRequest,
    AIFinancialHealthResponse,
    AIHistoryListResponse,
    AIHistoryResponse,
    AIInsightsResponse,
    AIPredictionRequest,
    AIPredictionResponse,
    AIRecommendationsResponse,
    AIScoreResponse,
    AISimulatorRequest,
    AISimulatorResponse,
    AISummaryRequest,
    AISummaryResponse,
)
from app.use_cases.ai.analyze import AIAnalyzeUseCase
from app.use_cases.ai.chat import AIChatUseCase
from app.use_cases.ai.financial_health import AIFinancialHealthUseCase
from app.use_cases.ai.insights import AIInsightsUseCase
from app.use_cases.ai.predictions import AIPredictionsUseCase
from app.use_cases.ai.recommendations import AIRecommendationsUseCase
from app.use_cases.ai.score import AIScoreUseCase
from app.use_cases.ai.simulator import AISimulatorUseCase
from app.use_cases.ai.summary import AISummaryUseCase
from app.services.ai.service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    data: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-100: Responde preguntas en lenguaje natural."""
    use_case = AIChatUseCase(db)
    return await use_case.execute(current_user.id, data.question)


@router.post("/analyze", response_model=AIAnalyzeResponse)
async def ai_analyze(
    data: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-098, FR-099, FR-107: Detecta patrones, anomalías y compara períodos."""
    use_case = AIAnalyzeUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.post("/predictions", response_model=AIPredictionResponse)
async def ai_predictions(
    data: AIPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-103, FR-104: Genera predicciones de ahorro y metas."""
    use_case = AIPredictionsUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.get("/insights", response_model=AIInsightsResponse)
async def ai_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-098, FR-099: Genera insights automáticos."""
    use_case = AIInsightsUseCase(db)
    return await use_case.execute(current_user.id)


@router.post("/score", response_model=AIScoreResponse)
async def ai_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-105: Calcula el Score Financiero."""
    use_case = AIScoreUseCase(db)
    return await use_case.execute(current_user.id)


@router.post("/recommendations", response_model=AIRecommendationsResponse)
async def ai_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-106, FR-108: Genera recomendaciones personalizadas."""
    use_case = AIRecommendationsUseCase(db)
    return await use_case.execute(current_user.id)


@router.post("/monthly-summary", response_model=AISummaryResponse)
async def ai_monthly_summary(
    data: AISummaryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-102: Genera resumen mensual."""
    use_case = AISummaryUseCase(db)
    return await use_case.execute(current_user.id, data, summary_type="monthly")


@router.post("/weekly-summary", response_model=AISummaryResponse)
async def ai_weekly_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-101: Genera resumen semanal."""
    use_case = AISummaryUseCase(db)
    data = AISummaryRequest()
    return await use_case.execute(current_user.id, data, summary_type="weekly")


@router.post("/financial-health", response_model=AIFinancialHealthResponse)
async def ai_financial_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Evalúa la salud financiera."""
    use_case = AIFinancialHealthUseCase(db)
    return await use_case.execute(current_user.id)


@router.post("/simulate", response_model=AISimulatorResponse)
async def ai_simulate(
    data: AISimulatorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Simula escenarios financieros."""
    use_case = AISimulatorUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.get("/history", response_model=AIHistoryListResponse)
async def ai_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Obtiene el historial de interacciones con la IA."""
    repo = AIHistoryRepository(db)
    items, total = await repo.list_by_user(current_user.id, page=page, limit=limit)
    data = [AIHistoryResponse.model_validate(h) for h in items]
    return AIHistoryListResponse(
        data=data,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
        },
    )


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_history(
    history_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Elimina una interacción del historial."""
    repo = AIHistoryRepository(db)
    history = await repo.get_by_user_and_id(current_user.id, history_id)
    if history:
        await repo.soft_delete(history)
        await db.commit()


@router.post("/feedback")
async def ai_feedback(
    data: AIFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Envía feedback sobre una respuesta de IA."""
    ai_service = AIService(db)
    await ai_service.add_feedback(current_user.id, data.history_id, data.feedback)
    return {"success": True, "message": "Feedback registrado"}
