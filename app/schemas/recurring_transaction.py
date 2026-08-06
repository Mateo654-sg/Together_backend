"""
Schemas Pydantic del módulo de Movimientos Recurrentes (FR-033).
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

FREQUENCIES = {"daily", "weekly", "monthly", "annual"}
RECURRING_TYPES = {"expense", "income"}


class CreateRecurringTransactionRequest(BaseModel):
    type: str = Field(..., max_length=20)
    frequency: str = Field(..., max_length=20)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: str = Field(..., min_length=1, max_length=255)
    category_id: uuid.UUID | None = None
    next_execution: date | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in RECURRING_TYPES:
            raise ValueError("El tipo debe ser expense o income.")
        return value

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, value: str) -> str:
        if value not in FREQUENCIES:
            raise ValueError("La frecuencia debe ser daily, weekly, monthly o annual.")
        return value


class UpdateRecurringTransactionRequest(BaseModel):
    type: str | None = Field(None, max_length=20)
    frequency: str | None = Field(None, max_length=20)
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    description: str | None = Field(None, min_length=1, max_length=255)
    category_id: uuid.UUID | None = None
    next_execution: date | None = None
    active: bool | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str | None) -> str | None:
        if value is not None and value not in RECURRING_TYPES:
            raise ValueError("El tipo debe ser expense o income.")
        return value

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, value: str | None) -> str | None:
        if value is not None and value not in FREQUENCIES:
            raise ValueError("La frecuencia debe ser daily, weekly, monthly o annual.")
        return value


class RecurringTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None
    type: str
    frequency: str
    amount: Decimal
    description: str
    next_execution: date
    last_executed: date | None
    active: bool
    created_at: datetime
    updated_at: datetime


class RecurringTransactionListResponse(BaseModel):
    data: list[RecurringTransactionResponse]
    pagination: dict


class ProcessRecurringResponse(BaseModel):
    executed: int
    details: list[dict]
