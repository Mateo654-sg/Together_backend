"""
Schemas Pydantic de transferencias entre métodos de pago (FR-021).
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.personal_finance import PAYMENT_METHOD_OPTIONS


class TransferRequest(BaseModel):
    from_method: str = Field(..., max_length=50)
    to_method: str = Field(..., max_length=50)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: str | None = Field(None, max_length=255)
    transfer_date: date

    @field_validator("from_method")
    @classmethod
    def validate_from_method(cls, value: str) -> str:
        if value not in PAYMENT_METHOD_OPTIONS:
            raise ValueError("Selecciona un método de pago válido.")
        return value

    @field_validator("to_method")
    @classmethod
    def validate_to_method(cls, value: str) -> str:
        if value not in PAYMENT_METHOD_OPTIONS:
            raise ValueError("Selecciona un método de pago válido.")
        return value


class CreateTransferRequest(TransferRequest):
    pass


class UpdateTransferRequest(BaseModel):
    from_method: str | None = Field(None, max_length=50)
    to_method: str | None = Field(None, max_length=50)
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    description: str | None = Field(None, max_length=255)
    transfer_date: date | None = None

    @field_validator("from_method", "to_method")
    @classmethod
    def validate_methods(cls, value: str | None) -> str | None:
        if value is not None and value not in PAYMENT_METHOD_OPTIONS:
            raise ValueError("Selecciona un método de pago válido.")
        return value


class TransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    from_method: str
    to_method: str
    amount: Decimal
    description: str | None
    transfer_date: date
    created_at: datetime
    updated_at: datetime


class TransferListResponse(BaseModel):
    data: list[TransferResponse]
    pagination: dict
