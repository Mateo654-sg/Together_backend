"""
Schemas Pydantic del módulo de Finanzas Compartidas (FR-041 a FR-060).

Incluye schemas para gastos compartidos, ingresos compartidos y deudas.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.shared_expense import SplitType


# ─── Shared Categories ─────────────────────────────────────────────────────────

class CreateSharedCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=7)


class SharedCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    icon: str | None
    color: str | None
    created_at: datetime


# ─── Shared Expenses ───────────────────────────────────────────────────────────

class CreateSharedExpenseRequest(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: str = Field(..., min_length=1, max_length=255)
    notes: str | None = None
    split_type: SplitType = SplitType.EQUAL
    split_details: str | None = None
    expense_date: date


class UpdateSharedExpenseRequest(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    description: str | None = Field(None, min_length=1, max_length=255)
    notes: str | None = None
    split_type: SplitType | None = None
    split_details: str | None = None
    expense_date: date | None = None


class SharedExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    couple_id: uuid.UUID
    category_id: uuid.UUID | None
    paid_by: uuid.UUID
    amount: Decimal
    description: str
    notes: str | None
    split_type: SplitType
    split_details: str | None
    expense_date: date
    attachment_url: str | None
    created_at: datetime
    updated_at: datetime


class SharedExpenseListResponse(BaseModel):
    data: list[SharedExpenseResponse]
    pagination: dict


# ─── Shared Incomes ────────────────────────────────────────────────────────────

class CreateSharedIncomeRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: str = Field(..., min_length=1, max_length=255)
    notes: str | None = None
    income_date: date


class SharedIncomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    couple_id: uuid.UUID
    received_by: uuid.UUID
    amount: Decimal
    description: str
    notes: str | None
    income_date: date
    created_at: datetime


class SharedIncomeListResponse(BaseModel):
    data: list[SharedIncomeResponse]
    pagination: dict


# ─── Debts ─────────────────────────────────────────────────────────────────────

class DebtResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    debtor_id: uuid.UUID
    creditor_id: uuid.UUID
    shared_expense_id: uuid.UUID | None
    amount: Decimal
    status: str
    created_at: datetime


class DebtListResponse(BaseModel):
    data: list[DebtResponse]
    pagination: dict


class PayDebtRequest(BaseModel):
    debt_id: uuid.UUID


# ─── Balance ───────────────────────────────────────────────────────────────────

class CoupleBalanceResponse(BaseModel):
    total_shared_expenses: Decimal
    total_shared_incomes: Decimal
    balance: Decimal
    partner_one_paid: Decimal
    partner_two_paid: Decimal
