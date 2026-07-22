"""
Schemas Pydantic del módulo de Pareja (FR-011 a FR-018).
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.couple import CoupleStatus
from app.schemas.user import UserResponse


class AcceptInvitationRequest(BaseModel):
    invitation_code: str = Field(..., min_length=6, max_length=12)


class RejectInvitationRequest(BaseModel):
    invitation_code: str = Field(..., min_length=6, max_length=12)


class CoupleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: CoupleStatus
    invitation_code: str
    partner_one_id: uuid.UUID
    partner_two_id: uuid.UUID | None
    created_at: datetime


class CoupleStatusResponse(BaseModel):
    """FR-015: Estado de la relación — sin pareja / pendiente / vinculada."""

    status: str  # "none" | "pending" | "accepted"
    couple: CoupleResponse | None = None
    partner: UserResponse | None = None
