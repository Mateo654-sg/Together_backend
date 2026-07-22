"""
Schemas Pydantic del módulo de Finanzas Personales (FR-019 a FR-040).

Incluye schemas para categorías, gastos e ingresos personales.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ─── Categories ────────────────────────────────────────────────────────────────

class CreateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=7)


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=7)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    icon: str | None
    color: str | None
    created_at: datetime


# ─── Personal Expenses ─────────────────────────────────────────────────────────

class CreateExpenseRequest(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: str = Field(..., min_length=1, max_length=255)
    notes: str | None = None
    payment_method: str | None = Field(None, max_length=50)
    location: str | None = Field(None, max_length=255)
    expense_date: date


class UpdateExpenseRequest(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    description: str | None = Field(None, min_length=1, max_length=255)
    notes: str | None = None
    payment_method: str | None = Field(None, max_length=50)
    location: str | None = Field(None, max_length=255)
    expense_date: date | None = None
    is_favorite: bool | None = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None
    amount: Decimal
    description: str
    notes: str | None
    payment_method: str | None
    location: str | None
    attachment_url: str | None
    expense_date: date
    is_favorite: bool
    created_at: datetime
    updated_at: datetime


class ExpenseListResponse(BaseModel):
    data: list[ExpenseResponse]
    pagination: dict


# ─── Personal Incomes ──────────────────────────────────────────────────────────

class CreateIncomeRequest(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: str = Field(..., min_length=1, max_length=255)
    notes: str | None = None
    income_date: date


class UpdateIncomeRequest(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    description: str | None = Field(None, min_length=1, max_length=255)
    notes: str | None = None
    income_date: date | None = None


class IncomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None
    amount: Decimal
    description: str
    notes: str | None
    income_date: date
    created_at: datetime
    updated_at: datetime


class IncomeListResponse(BaseModel):
    data: list[IncomeResponse]
    pagination: dict
