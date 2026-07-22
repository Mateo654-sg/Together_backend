"""
Router: /api/v1/incomes

Ingresos personales del usuario (FR-019).
"""
import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.personal_finance import (
    CreateIncomeRequest,
    IncomeListResponse,
    IncomeResponse,
    UpdateIncomeRequest,
)
from app.use_cases.personal_finance.create_income import CreateIncomeUseCase
from app.use_cases.personal_finance.delete_income import DeleteIncomeUseCase
from app.use_cases.personal_finance.list_incomes import ListIncomesUseCase
from app.use_cases.personal_finance.update_income import UpdateIncomeUseCase

router = APIRouter(prefix="/incomes", tags=["Personal Incomes"])


@router.get("", response_model=IncomeListResponse)
async def list_incomes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    category_id: uuid.UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """Lista ingresos personales con soporte para filtros y paginación."""
    use_case = ListIncomesUseCase(db)
    return await use_case.execute(
        current_user.id,
        page=page,
        limit=limit,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.post("", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    data: CreateIncomeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-019: Registra un ingreso personal nuevo."""
    use_case = CreateIncomeUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: uuid.UUID,
    data: UpdateIncomeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-022: Editar un ingreso personal existente."""
    use_case = UpdateIncomeUseCase(db)
    return await use_case.execute(current_user.id, income_id, data)


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    income_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-023: Eliminar un ingreso personal (soft delete)."""
    use_case = DeleteIncomeUseCase(db)
    await use_case.execute(current_user.id, income_id)
