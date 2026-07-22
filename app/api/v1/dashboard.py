"""
Router: /api/v1/dashboard

Dashboard principal y de pareja (FR-079 a FR-088).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import CoupleDashboardResponse, DashboardResponse
from app.use_cases.dashboard.get_couple_dashboard import GetCoupleDashboardUseCase
from app.use_cases.dashboard.get_dashboard import GetDashboardUseCase

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-079 a FR-088: Dashboard principal con resumen de finanzas."""
    use_case = GetDashboardUseCase(db)
    return await use_case.execute(current_user.id)


@router.get("/couple", response_model=CoupleDashboardResponse)
async def get_couple_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard de pareja con datos compartidos."""
    use_case = GetCoupleDashboardUseCase(db)
    return await use_case.execute(current_user.id)
