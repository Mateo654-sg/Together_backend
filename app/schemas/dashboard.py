"""
Schemas Pydantic del módulo de Dashboard (FR-079 a FR-088).

Incluye schemas para el resumen principal y datos agregados.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# ─── Dashboard Summary ─────────────────────────────────────────────────────────

class DashboardGoalSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    target_amount: Decimal
    current_amount: Decimal
    progress_percentage: float
    target_date: datetime | None = None
    status: str


class DashboardRecentActivity(BaseModel):
    id: uuid.UUID
    type: str  # "expense", "income", "contribution"
    description: str
    amount: Decimal
    date: datetime
    category: str | None = None


class DashboardUpcomingPayment(BaseModel):
    id: uuid.UUID
    type: str  # "expense", "debt", "budget"
    description: str
    amount: Decimal
    due_date: datetime
    status: str


class DashboardResponse(BaseModel):
    balance: Decimal
    income: Decimal
    expense: Decimal
    saving: Decimal
    cash_flow: Decimal
    goals: list[DashboardGoalSummary]
    statistics: dict
    recent_activity: list[DashboardRecentActivity]
    upcoming_payments: list[DashboardUpcomingPayment]
    ai_recommendations: list[str]


class CoupleDashboardResponse(BaseModel):
    personal_balance: Decimal
    shared_balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    shared_income: Decimal
    shared_expense: Decimal
    saving: Decimal
    goals: list[DashboardGoalSummary]
    statistics: dict
    recent_activity: list[DashboardRecentActivity]
    upcoming_payments: list[DashboardUpcomingPayment]
    ai_recommendations: list[str]
