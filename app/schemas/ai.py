"""
Schemas Pydantic del módulo de IA Financiera (FR-098 a FR-108).

Incluye schemas para chat, análisis, predicciones, score, insights, recomendaciones.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ─── Chat ──────────────────────────────────────────────────────────────────────

class AIChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class AIChatResponse(BaseModel):
    answer: str
    tokens_used: int = 0
    provider: str = "mock"


# ─── Analyze ───────────────────────────────────────────────────────────────────

class AIAnalyzeRequest(BaseModel):
    analysis_type: str = Field(
        ..., description="patterns, anomalies, comparison, categories"
    )
    month: int | None = Field(None, ge=1, le=12)
    year: int | None = Field(None, ge=2020, le=2100)
    compare_month: int | None = Field(None, ge=1, le=12)
    compare_year: int | None = Field(None, ge=2020, le=2100)


class AIAnalyzeResponse(BaseModel):
    analysis_type: str
    result: dict
    insights: list[str]


# ─── Predictions ───────────────────────────────────────────────────────────────

class AIPredictionRequest(BaseModel):
    prediction_type: str = Field(
        ..., description="savings, goal_completion, cash_flow, balance"
    )
    goal_id: uuid.UUID | None = None
    months_ahead: int = Field(3, ge=1, le=12)


class AIPredictionResponse(BaseModel):
    prediction_type: str
    predictions: list[dict]
    confidence: float
    recommendations: list[str]


# ─── Financial Score ───────────────────────────────────────────────────────────

class AIScoreResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    grade: str  # "Excellent", "Good", "Fair", "Poor"
    factors: list[dict]
    recommendations: list[str]


# ─── Insights ──────────────────────────────────────────────────────────────────

class AIInsightsResponse(BaseModel):
    insights: list[dict]
    period: str


# ─── Recommendations ──────────────────────────────────────────────────────────

class AIRecommendationsResponse(BaseModel):
    recommendations: list[dict]
    potential_savings: Decimal


# ─── Summaries ────────────────────────────────────────────────────────────────

class AISummaryRequest(BaseModel):
    month: int | None = Field(None, ge=1, le=12)
    year: int | None = Field(None, ge=2020, le=2100)


class AISummaryResponse(BaseModel):
    period: str
    summary: str
    highlights: list[str]
    kpis: dict


# ─── Financial Health ─────────────────────────────────────────────────────────

class AIFinancialHealthResponse(BaseModel):
    status: str  # "Excellent", "Good", "Fair", "Critical"
    score: int
    indicators: dict
    recommendations: list[str]


# ─── Simulator ────────────────────────────────────────────────────────────────

class AISimulatorRequest(BaseModel):
    scenario: str = Field(..., min_length=1, max_length=500)
    monthly_amount: Decimal | None = None
    months: int = Field(6, ge=1, le=24)


class AISimulatorResponse(BaseModel):
    scenario: str
    current_projection: dict
    simulated_projection: dict
    difference: dict
    recommendation: str


# ─── History ───────────────────────────────────────────────────────────────────

class AIHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question: str
    answer: str
    endpoint: str
    tokens_input: int
    tokens_output: int
    cost_usd: float
    provider: str
    model: str
    response_time_ms: int
    feedback: int | None = None
    created_at: datetime


class AIHistoryListResponse(BaseModel):
    data: list[AIHistoryResponse]
    pagination: dict


# ─── Feedback └─────────────────────────────────────────────────────────────────

class AIFeedbackRequest(BaseModel):
    history_id: uuid.UUID
    feedback: int = Field(..., description="1 for positive, -1 for negative")
