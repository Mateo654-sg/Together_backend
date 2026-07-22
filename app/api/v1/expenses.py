"""
Router: /api/v1/expenses

Gastos personales del usuario (FR-020 a FR-040).
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.personal_finance import (
    CreateExpenseRequest,
    ExpenseListResponse,
    ExpenseResponse,
    UpdateExpenseRequest,
)
from app.use_cases.personal_finance.create_expense import CreateExpenseUseCase
from app.use_cases.personal_finance.delete_expense import DeleteExpenseUseCase
from app.use_cases.personal_finance.duplicate_expense import DuplicateExpenseUseCase
from app.use_cases.personal_finance.get_balance import GetPersonalBalanceUseCase
from app.use_cases.personal_finance.get_expense import GetExpenseUseCase
from app.use_cases.personal_finance.list_expenses import ListExpensesUseCase
from app.use_cases.personal_finance.update_expense import UpdateExpenseUseCase

router = APIRouter(prefix="/expenses", tags=["Personal Expenses"])


@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-040: Consultar saldo personal (ingresos - gastos)."""
    use_case = GetPersonalBalanceUseCase(db)
    balance = await use_case.execute(current_user.id)
    return {"balance": balance}


@router.get("", response_model=ExpenseListResponse)
async def list_expenses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    category_id: uuid.UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("expense_date"),
    sort_order: str = Query("desc"),
):
    """FR-036/FR-037/FR-038/FR-039: Lista gastos con filtros, búsqueda y paginación."""
    use_case = ListExpensesUseCase(db)
    return await use_case.execute(
        current_user.id,
        page=page,
        limit=limit,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-039: Obtiene un gasto específico por ID."""
    use_case = GetExpenseUseCase(db)
    return await use_case.execute(current_user.id, expense_id)


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: CreateExpenseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-020: Registra un gasto personal nuevo."""
    use_case = CreateExpenseUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: uuid.UUID,
    data: UpdateExpenseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-022: Editar un gasto personal existente."""
    use_case = UpdateExpenseUseCase(db)
    return await use_case.execute(current_user.id, expense_id, data)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-023: Eliminar un gasto personal (soft delete)."""
    use_case = DeleteExpenseUseCase(db)
    await use_case.execute(current_user.id, expense_id)


@router.post(
    "/duplicate", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED
)
async def duplicate_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-034: Duplicar un gasto existente con la fecha de hoy."""
    use_case = DuplicateExpenseUseCase(db)
    return await use_case.execute(current_user.id, expense_id)
