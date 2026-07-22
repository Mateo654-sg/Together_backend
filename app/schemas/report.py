"""
Schemas Pydantic del módulo de Reportes y Estadísticas (FR-089 a FR-098).

Incluye schemas para reportes y estadísticas.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ─── Reports ───────────────────────────────────────────────────────────────────

class GenerateReportRequest(BaseModel):
    report_type: str = Field(..., description="monthly, yearly, weekly, category, personal, couple")
    format: str = Field("pdf", description="pdf, excel, csv")
    month: int | None = Field(None, ge=1, le=12)
    year: int | None = Field(None, ge=2020, le=2100)
    category_id: uuid.UUID | None = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    report_type: str
    format: str
    status: str
    file_path: str | None = None
    parameters: str | None = None
    generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ReportListResponse(BaseModel):
    data: list[ReportResponse]
    pagination: dict


# ─── Statistics ────────────────────────────────────────────────────────────────

class MonthlyStatisticsResponse(BaseModel):
    month: int
    year: int
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    savings_rate: float
    top_categories: list[dict]
    daily_average_expense: Decimal


class YearlyStatisticsResponse(BaseModel):
    year: int
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    savings_rate: float
    monthly_breakdown: list[dict]
    top_categories: list[dict]


class CategoryStatisticsResponse(BaseModel):
    category_id: uuid.UUID
    category_name: str
    total_amount: Decimal
    percentage_of_total: float
    transaction_count: int


class CoupleStatisticsResponse(BaseModel):
    personal_income: Decimal
    personal_expense: Decimal
    shared_income: Decimal
    shared_expense: Decimal
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    savings_rate: float
    partner_contribution: dict


class PersonalStatisticsResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    savings_rate: float
    top_expense_categories: list[dict]
    top_income_categories: list[dict]
    monthly_trend: list[dict]
