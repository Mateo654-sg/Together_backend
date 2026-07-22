"""
Router: /api/v1/shared-incomes

Ingresos compartidos entre la pareja (FR-042).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.shared_finance import (
    CreateSharedIncomeRequest,
    SharedIncomeListResponse,
    SharedIncomeResponse,
)
from app.use_cases.shared_finance.create_shared_income import CreateSharedIncomeUseCase
from app.use_cases.shared_finance.list_shared_incomes import ListSharedIncomesUseCase

router = APIRouter(prefix="/shared-incomes", tags=["Shared Incomes"])


@router.get("", response_model=SharedIncomeListResponse)
async def list_shared_incomes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Lista ingresos compartidos de la pareja."""
    use_case = ListSharedIncomesUseCase(db)
    return await use_case.execute(current_user.id, page=page, limit=limit)


@router.post(
    "", response_model=SharedIncomeResponse, status_code=status.HTTP_201_CREATED
)
async def create_shared_income(
    data: CreateSharedIncomeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-042: Registra un ingreso compartido."""
    use_case = CreateSharedIncomeUseCase(db)
    return await use_case.execute(current_user.id, data)
