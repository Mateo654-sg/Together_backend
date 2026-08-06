"""
Router: /api/v1/transfers

Transferencias entre métodos de pago del usuario (FR-021).
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
from app.schemas.transfer import (
    CreateTransferRequest,
    TransferListResponse,
    TransferResponse,
    UpdateTransferRequest,
)
from app.use_cases.transfers import (
    CreateTransferUseCase,
    DeleteTransferUseCase,
    GetTransferUseCase,
    ListTransfersUseCase,
    UpdateTransferUseCase,
)

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.get("", response_model=TransferListResponse)
async def list_transfers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    method: str | None = Query(None),
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
):
    """FR-021: Lista transferencias del usuario con filtros y paginación."""
    use_case = ListTransfersUseCase(db)
    return await use_case.execute(
        current_user.id,
        page=page,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        method=method,
        min_amount=min_amount,
        max_amount=max_amount,
    )


@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(
    transfer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-021: Obtiene una transferencia específica por ID."""
    use_case = GetTransferUseCase(db)
    return await use_case.execute(current_user.id, transfer_id)


@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    data: CreateTransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-021: Registra una transferencia entre métodos de pago."""
    use_case = CreateTransferUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{transfer_id}", response_model=TransferResponse)
async def update_transfer(
    transfer_id: uuid.UUID,
    data: UpdateTransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-021: Edita una transferencia existente."""
    use_case = UpdateTransferUseCase(db)
    return await use_case.execute(current_user.id, transfer_id, data)


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transfer(
    transfer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-021: Elimina una transferencia (soft delete)."""
    use_case = DeleteTransferUseCase(db)
    await use_case.execute(current_user.id, transfer_id)
