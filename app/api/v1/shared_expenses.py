"""
Router: /api/v1/shared-expenses

Gastos compartidos entre la pareja (FR-041 a FR-054).
"""
import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.shared_finance import (
    CreateSharedExpenseRequest,
    SharedExpenseListResponse,
    SharedExpenseResponse,
    UpdateSharedExpenseRequest,
)
from app.use_cases.shared_finance.create_shared_expense import CreateSharedExpenseUseCase
from app.use_cases.shared_finance.delete_shared_expense import DeleteSharedExpenseUseCase
from app.use_cases.shared_finance.list_shared_expenses import ListSharedExpensesUseCase
from app.use_cases.shared_finance.update_shared_expense import (
    UpdateSharedExpenseUseCase,
)

router = APIRouter(prefix="/shared-expenses", tags=["Shared Expenses"])


@router.get("", response_model=SharedExpenseListResponse)
async def list_shared_expenses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    category_id: uuid.UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """FR-052: Lista gastos compartidos con filtros y paginación."""
    use_case = ListSharedExpensesUseCase(db)
    return await use_case.execute(
        current_user.id,
        page=page,
        limit=limit,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.post(
    "", response_model=SharedExpenseResponse, status_code=status.HTTP_201_CREATED
)
async def create_shared_expense(
    data: CreateSharedExpenseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-041: Registra un gasto compartido con división automática."""
    use_case = CreateSharedExpenseUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{expense_id}", response_model=SharedExpenseResponse)
async def update_shared_expense(
    expense_id: uuid.UUID,
    data: UpdateSharedExpenseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-053: Editar un gasto compartido."""
    use_case = UpdateSharedExpenseUseCase(db)
    return await use_case.execute(current_user.id, expense_id, data)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shared_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-054: Eliminar un gasto compartido (cancela deudas asociadas)."""
    use_case = DeleteSharedExpenseUseCase(db)
    await use_case.execute(current_user.id, expense_id)
