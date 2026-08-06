"""
Use Case: CancelInvitation (FR-011, FR-012).

Permite que el emisor cancele una invitación pendiente: el código deja
de ser válido y el usuario vuelve a estar sin pareja.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.couple import Couple, CoupleStatus
from app.repositories.couple_repository import CoupleRepository


class CancelInvitationUseCase:
    """Use Case: CancelInvitation (FR-011, FR-012).

    Cancela la invitación pendiente del usuario emisor marcándola como
    REJECTED. Como REJECTED no es un estado activo, el código deja de ser
    válido y el usuario vuelve al estado "sin pareja" (none).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID) -> Couple:
        """Cancela la invitación pendiente del usuario.

        Args:
            user_id: UUID del usuario que cancela su invitación.

        Returns:
            La relación de pareja con estado actualizado a REJECTED.

        Raises:
            NotFoundException: Si el usuario no tiene una invitación pendiente.
            ConflictException: Si la relación no está en estado pendiente.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None:
            raise NotFoundException(
                "No tienes una invitación pendiente para cancelar."
            )

        if couple.status != CoupleStatus.PENDING:
            raise ConflictException(
                "Solo puedes cancelar una invitación pendiente."
            )

        if couple.partner_one_id != user_id:
            raise ConflictException(
                "No puedes cancelar una invitación que no creaste."
            )

        couple.status = CoupleStatus.REJECTED
        await self.session.commit()
        return couple
