"""
Schemas Pydantic del módulo de usuarios.
"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    avatar_url: str | None
    birth_date: date | None
    phone: str | None
    language: str
    currency: str
    timezone: str
    is_verified: bool
    last_login: datetime | None
    created_at: datetime


class UpdateUserRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    phone: str | None = None
    language: str | None = None
    currency: str | None = None
    timezone: str | None = None


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    theme: str
    biometric_enabled: bool
    notifications_enabled: bool
    reminder_enabled: bool
    ai_enabled: bool
    default_home_screen: str


class UpdateUserSettingsRequest(BaseModel):
    theme: str | None = None
    biometric_enabled: bool | None = None
    notifications_enabled: bool | None = None
    reminder_enabled: bool | None = None
    ai_enabled: bool | None = None
    default_home_screen: str | None = None


class UpdateAvatarRequest(BaseModel):
    avatar_url: str = Field(..., max_length=500)


class UserStatisticsResponse(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    total_categories_used: int
    total_expenses_count: int
    total_incomes_count: int


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class SessionHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device: str | None
    ip: str | None
    is_revoked: bool
    created_at: datetime
    expires_at: datetime


class SessionHistoryResponse(BaseModel):
    data: list[SessionHistoryItem]
