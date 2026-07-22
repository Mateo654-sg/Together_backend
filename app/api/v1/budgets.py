"""
Router: /api/v1/budgets

Presupuestos del usuario (FR-073 a FR-078).
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.budget import (
    BudgetAlertListResponse,
    BudgetListResponse,
    BudgetResponse,
    CreateBudgetRequest,
    UpdateBudgetRequest,
)
from app.use_cases.budgets.create_budget import CreateBudgetUseCase
from app.use_cases.budgets.delete_budget import DeleteBudgetUseCase
from app.use_cases.budgets.get_budget_alerts import GetBudgetAlertsUseCase
from app.use_cases.budgets.list_budgets import ListBudgetsUseCase
from app.use_cases.budgets.update_budget import UpdateBudgetUseCase

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=BudgetListResponse)
async def list_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2020, le=2100),
    category_id: uuid.UUID | None = Query(None),
):
    """FR-073: Lista presupuestos con filtros y paginación."""
    use_case = ListBudgetsUseCase(db)
    return await use_case.execute(
        current_user.id, page=page, limit=limit, month=month, year=year, category_id=category_id
    )


@router.post(
    "", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED
)
async def create_budget(
    data: CreateBudgetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-073 a FR-076: Crea un nuevo presupuesto."""
    use_case = CreateBudgetUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: uuid.UUID,
    data: UpdateBudgetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-073 a FR-076: Editar un presupuesto existente."""
    use_case = UpdateBudgetUseCase(db)
    return await use_case.execute(current_user.id, budget_id, data)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Eliminar un presupuesto (soft delete)."""
    use_case = DeleteBudgetUseCase(db)
    await use_case.execute(current_user.id, budget_id)


@router.get("/alerts", response_model=BudgetAlertListResponse)
async def get_budget_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2020, le=2100),
):
    """FR-077, FR-078: Obtener alertas de presupuestos (80%, 90%, 100%)."""
    use_case = GetBudgetAlertsUseCase(db)
    return await use_case.execute(current_user.id, month=month, year=year)
