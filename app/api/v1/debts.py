"""
Router: /api/v1/debts

Deudas entre la pareja (FR-050, FR-055, FR-059).
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.shared_finance import CoupleBalanceResponse, DebtResponse
from app.use_cases.shared_finance.get_couple_balance import GetCoupleBalanceUseCase
from app.use_cases.shared_finance.list_debt_history import ListDebtHistoryUseCase
from app.use_cases.shared_finance.list_debts import ListDebtsUseCase
from app.use_cases.shared_finance.pay_debt import PayDebtUseCase

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.get("", response_model=list[DebtResponse])
async def list_debts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-051: Lista deudas pendientes del usuario."""
    use_case = ListDebtsUseCase(db)
    return await use_case.execute(current_user.id)


@router.get("/history", response_model=list[DebtResponse])
async def list_debt_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-052: Historial completo de deudas de la pareja."""
    use_case = ListDebtHistoryUseCase(db)
    return await use_case.execute(current_user.id)


@router.post("/{debt_id}/pay", response_model=DebtResponse)
async def pay_debt(
    debt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-055/FR-059: Marca una deuda como pagada."""
    use_case = PayDebtUseCase(db)
    return await use_case.execute(current_user.id, debt_id)


@router.get("/balance", response_model=CoupleBalanceResponse)
async def get_couple_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-051: Balance financiero entre la pareja."""
    use_case = GetCoupleBalanceUseCase(db)
    return await use_case.execute(current_user.id)
