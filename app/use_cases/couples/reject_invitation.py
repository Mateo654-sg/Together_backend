"""
Use Case: RejectInvitation (FR-014).
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.models.couple import Couple, CoupleStatus
from app.repositories.couple_repository import CoupleRepository


class RejectInvitationUseCase:
    """Use Case: RejectInvitation (FR-014).

    Permite rechazar una invitación de pareja recibida.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID, invitation_code: str) -> Couple:
        """Rechaza una invitación de pareja.

        Args:
            user_id: UUID del usuario que rechaza la invitación.
            invitation_code: Código de invitación a rechazar.

        Returns:
            La relación de pareja con el estado actualizado a REJECTED.

        Raises:
            NotFoundException: Si el código de invitación no es válido.
            ConflictException: Si la invitación ya no está disponible.
            ValidationException: Si el usuario intenta rechazar su propia invitación.
        """
        couple = await self.couple_repository.get_by_invitation_code(invitation_code)
        if couple is None:
            raise NotFoundException("Código de invitación no válido.")

        if couple.status != CoupleStatus.PENDING:
            raise ConflictException("Esta invitación ya no está disponible.")

        if couple.partner_one_id == user_id:
            raise ValidationException("No puedes rechazar tu propia invitación.")

        couple.status = CoupleStatus.REJECTED
        await self.session.commit()
        return couple
