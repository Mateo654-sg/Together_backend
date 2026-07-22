"""
Schemas Pydantic del módulo de Metas (FR-061 a FR-072).

Incluye schemas para metas y aportes.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ─── Goals ─────────────────────────────────────────────────────────────────────

class CreateGoalRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    image: str | None = Field(None, max_length=500)
    target_amount: Decimal = Field(..., gt=0, decimal_places=2)
    target_date: date | None = None


class UpdateGoalRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    image: str | None = Field(None, max_length=500)
    target_amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    target_date: date | None = None
    status: str | None = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    couple_id: uuid.UUID
    title: str
    description: str | None
    image: str | None
    target_amount: Decimal
    current_amount: Decimal
    target_date: date | None
    status: str
    progress_percentage: float | None = None
    days_remaining: int | None = None
    predicted_completion_date: date | None = None
    created_at: datetime
    updated_at: datetime


class GoalListResponse(BaseModel):
    data: list[GoalResponse]
    pagination: dict


# ─── Goal Contributions ────────────────────────────────────────────────────────

class CreateContributionRequest(BaseModel):
    goal_id: uuid.UUID
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    contribution_date: date | None = None


class ContributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    goal_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    contribution_date: datetime
    created_at: datetime | None = None


class ContributionListResponse(BaseModel):
    data: list[ContributionResponse]
    pagination: dict


# ─── Goal Statistics ───────────────────────────────────────────────────────────

class GoalStatisticsResponse(BaseModel):
    total_goals: int
    active_goals: int
    completed_goals: int
    total_saved: Decimal
    total_target: Decimal
    overall_progress_percentage: float
    goals_on_track: int
    goals_behind: int
