"""
Schemas Pydantic del módulo de Presupuestos (FR-073 a FR-078).

Incluye schemas para presupuestos y alertas.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ─── Budgets ───────────────────────────────────────────────────────────────────

class CreateBudgetRequest(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)


class UpdateBudgetRequest(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    month: int | None = Field(None, ge=1, le=12)
    year: int | None = Field(None, ge=2020, le=2100)


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None
    amount: Decimal
    month: int
    year: int
    spent: Decimal | None = None
    percentage_consumed: float | None = None
    created_at: datetime
    updated_at: datetime


class BudgetListResponse(BaseModel):
    data: list[BudgetResponse]
    pagination: dict


# ─── Budget Alerts ─────────────────────────────────────────────────────────────

class BudgetAlertResponse(BaseModel):
    budget_id: uuid.UUID
    category_id: uuid.UUID | None
    amount: Decimal
    spent: Decimal
    percentage: float
    level: str  # "warning", "critical", "exceeded"
    month: int
    year: int


class BudgetAlertListResponse(BaseModel):
    data: list[BudgetAlertResponse]
