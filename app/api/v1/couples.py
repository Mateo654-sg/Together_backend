"""
Router: /api/v1/couples (Módulo 2 — Pareja, FR-011 a FR-018).
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.couple import (
    AcceptInvitationRequest,
    CoupleResponse,
    CoupleStatusResponse,
    RejectInvitationRequest,
)
from app.use_cases.couples.accept_invitation import AcceptInvitationUseCase
from app.use_cases.couples.create_invitation import CreateInvitationUseCase
from app.use_cases.couples.get_couple_status import GetCoupleStatusUseCase
from app.use_cases.couples.reject_invitation import RejectInvitationUseCase
from app.use_cases.couples.unlink_couple import UnlinkCoupleUseCase

router = APIRouter(prefix="/couples", tags=["Couples"])


@router.get("", response_model=CoupleStatusResponse)
async def get_couple_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-015: Estado de la relación — sin pareja / pendiente / vinculada."""
    use_case = GetCoupleStatusUseCase(db)
    return await use_case.execute(current_user.id)


@router.post("/invite", response_model=CoupleResponse, status_code=status.HTTP_201_CREATED)
async def invite_partner(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-011/FR-012: Genera un código único y envía una invitación."""
    use_case = CreateInvitationUseCase(db)
    return await use_case.execute(current_user.id)


@router.post("/accept", response_model=CoupleResponse)
async def accept_invitation(
    data: AcceptInvitationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-013: Aceptar una invitación mediante código."""
    use_case = AcceptInvitationUseCase(db)
    return await use_case.execute(current_user.id, data.invitation_code)


@router.post("/reject", response_model=CoupleResponse)
async def reject_invitation(
    data: RejectInvitationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-014: Rechazar una invitación mediante código."""
    use_case = RejectInvitationUseCase(db)
    return await use_case.execute(current_user.id, data.invitation_code)


@router.delete("/unlink", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_couple(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-018: Desvincular la pareja."""
    use_case = UnlinkCoupleUseCase(db)
    await use_case.execute(current_user.id)
