"""
Router: /api/v1/statistics

Estadísticas financieras (FR-089 a FR-098).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.report import (
    MonthlyStatisticsResponse,
    PersonalStatisticsResponse,
)
from app.use_cases.reports.get_monthly_statistics import GetMonthlyStatisticsUseCase
from app.use_cases.reports.get_personal_statistics import GetPersonalStatisticsUseCase

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/month", response_model=MonthlyStatisticsResponse)
async def get_monthly_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2020, le=2100),
):
    """FR-089: Estadísticas del mes."""
    use_case = GetMonthlyStatisticsUseCase(db)
    return await use_case.execute(current_user.id, month=month, year=year)


@router.get("/personal", response_model=PersonalStatisticsResponse)
async def get_personal_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-092: Estadísticas personales."""
    use_case = GetPersonalStatisticsUseCase(db)
    return await use_case.execute(current_user.id)
