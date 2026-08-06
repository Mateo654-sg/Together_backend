"""
Router: /api/v1/recurring

Movimientos recurrentes automáticos (FR-033).
"""
import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.recurring_transaction import (
    CreateRecurringTransactionRequest,
    ProcessRecurringResponse,
    RecurringTransactionListResponse,
    RecurringTransactionResponse,
    UpdateRecurringTransactionRequest,
)
from app.use_cases.recurring.create_recurring_transaction import (
    CreateRecurringTransactionUseCase,
)
from app.use_cases.recurring.delete_recurring_transaction import (
    DeleteRecurringTransactionUseCase,
)
from app.use_cases.recurring.list_recurring_transactions import (
    ListRecurringTransactionsUseCase,
)
from app.use_cases.recurring.process_due_recurring import (
    ProcessDueRecurringTransactionsUseCase,
)
from app.use_cases.recurring.update_recurring_transaction import (
    UpdateRecurringTransactionUseCase,
)

router = APIRouter(prefix="/recurring", tags=["Recurring Transactions"])


@router.get("", response_model=RecurringTransactionListResponse)
async def list_recurring(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    active: bool | None = Query(None),
):
    """FR-033: Lista movimientos recurrentes con paginación y filtro."""
    use_case = ListRecurringTransactionsUseCase(db)
    return await use_case.execute(
        current_user.id, page=page, limit=limit, active=active
    )


@router.post(
    "", response_model=RecurringTransactionResponse, status_code=status.HTTP_201_CREATED
)
async def create_recurring(
    data: CreateRecurringTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-033: Crea un movimiento recurrente (diario, semanal, mensual o anual)."""
    use_case = CreateRecurringTransactionUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.post(
    "/process",
    response_model=ProcessRecurringResponse,
)
async def process_recurring(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    on_date: date | None = Query(None),
):
    """FR-033: Materializa las recurrencias vencidas en movimientos reales."""
    use_case = ProcessDueRecurringTransactionsUseCase(db)
    return await use_case.execute(current_user.id, on_date)


@router.put("/{recurring_id}", response_model=RecurringTransactionResponse)
async def update_recurring(
    recurring_id: uuid.UUID,
    data: UpdateRecurringTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-033: Edita un movimiento recurrente existente."""
    use_case = UpdateRecurringTransactionUseCase(db)
    return await use_case.execute(current_user.id, recurring_id, data)


@router.delete("/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring(
    recurring_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-033: Elimina un movimiento recurrente (soft delete)."""
    use_case = DeleteRecurringTransactionUseCase(db)
    await use_case.execute(current_user.id, recurring_id)
