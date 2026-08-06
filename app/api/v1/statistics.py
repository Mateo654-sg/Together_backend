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
    CategoryStatisticsResponse,
    CoupleStatisticsResponse,
    MonthlyStatisticsResponse,
    PersonalStatisticsResponse,
    YearlyStatisticsResponse,
)
from app.use_cases.reports.get_category_statistics import GetCategoryStatisticsUseCase
from app.use_cases.reports.get_couple_statistics import GetCoupleStatisticsUseCase
from app.use_cases.reports.get_monthly_statistics import GetMonthlyStatisticsUseCase
from app.use_cases.reports.get_personal_statistics import GetPersonalStatisticsUseCase
from app.use_cases.reports.get_yearly_statistics import GetYearlyStatisticsUseCase

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


@router.get("/year", response_model=YearlyStatisticsResponse)
async def get_yearly_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    year: int | None = Query(None, ge=2020, le=2100),
):
    """FR-090: Estadísticas del año."""
    use_case = GetYearlyStatisticsUseCase(db)
    return await use_case.execute(current_user.id, year=year)


@router.get("/category", response_model=list[CategoryStatisticsResponse])
async def get_category_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2020, le=2100),
    type: str = Query("expense", pattern="^(expense|income)$"),
):
    """FR-091: Estadísticas por categoría."""
    use_case = GetCategoryStatisticsUseCase(db)
    return await use_case.execute(
        current_user.id, month=month, year=year, type=type
    )


@router.get("/couple", response_model=CoupleStatisticsResponse)
async def get_couple_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-093: Estadísticas de la pareja."""
    use_case = GetCoupleStatisticsUseCase(db)
    return await use_case.execute(current_user.id)


@router.get("/personal", response_model=PersonalStatisticsResponse)
async def get_personal_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-092: Estadísticas personales."""
    use_case = GetPersonalStatisticsUseCase(db)
    return await use_case.execute(current_user.id)
