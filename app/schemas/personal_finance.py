"""
Schemas Pydantic del módulo de Finanzas Personales (FR-019 a FR-040).

Incluye schemas para categorías, gastos e ingresos personales.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.tag import TagResponse


PAYMENT_METHOD_OPTIONS = {
    "Efectivo",
    "Nequi",
    "Nu",
    "Bancolombia",
    "Davivienda",
    "BBVA",
    "Banco de Bogotá",
    "Caja Social",
    "Banco AV Villas",
    "Banco Popular",
    "Colpatria",
    "PSE",
    "Tarjeta Débito",
    "Tarjeta Crédito",
    "Otro",
}


class PaymentMethodValidator(BaseModel):
    @field_validator("payment_method", check_fields=False)
    @classmethod
    def validate_payment_method(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in PAYMENT_METHOD_OPTIONS:
            raise ValueError("Selecciona un método de pago válido.")
        return value


# ─── Categories ────────────────────────────────────────────────────────────────

class CreateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=7)
    type: str = Field("expense", max_length=20)


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=7)
    type: str | None = Field(None, max_length=20)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    icon: str | None
    color: str | None
    type: str
    created_at: datetime


# ─── Personal Expenses ─────────────────────────────────────────────────────────

class CreateExpenseRequest(PaymentMethodValidator):
    category_id: uuid.UUID | None = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: str = Field(..., min_length=1, max_length=255)
    notes: str | None = None
    payment_method: str | None = Field(None, max_length=50)
    location: str | None = Field(None, max_length=255)
    expense_date: date
    tag_ids: list[uuid.UUID] = Field(default_factory=list)


class UpdateExpenseRequest(PaymentMethodValidator):
    category_id: uuid.UUID | None = None
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    description: str | None = Field(None, min_length=1, max_length=255)
    notes: str | None = None
    payment_method: str | None = Field(None, max_length=50)
    location: str | None = Field(None, max_length=255)
    expense_date: date | None = None
    is_favorite: bool | None = None
    tag_ids: list[uuid.UUID] | None = None


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
    tags: list[TagResponse] = Field(default_factory=list)
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
