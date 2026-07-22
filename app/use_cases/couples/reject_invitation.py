"""
Use Case: RejectInvitation (FR-014).
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.couple import Couple, CoupleStatus
from app.repositories.couple_repository import CoupleRepository


class RejectInvitationUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID, invitation_code: str) -> Couple:
        couple = await self.couple_repository.get_by_invitation_code(invitation_code)
        if couple is None:
            raise NotFoundException("Código de invitación no válido.")

        if couple.status != CoupleStatus.PENDING:
            raise ConflictException("Esta invitación ya no está disponible.")

        if couple.partner_one_id == user_id:
            raise ValidationException("No puedes rechazar tu propia invitación.")

        couple.status = CoupleStatus.REJECTED
        await self.session.commit()
        await self.couple_repository.refresh(couple)
        return couple
