"""
Use Case: AcceptInvitation (FR-013).

Al aceptar, se habilita el espacio compartido (FR-016): gastos
compartidos, metas compartidas, dashboard conjunto, IA compartida.
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


class AcceptInvitationUseCase:
    """Use Case: AcceptInvitation (FR-013).

    Al aceptar, se habilita el espacio compartido (FR-016): gastos
    compartidos, metas compartidas, dashboard conjunto, IA compartida.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID, invitation_code: str) -> Couple:
        """Acepta una invitación de pareja y activa el espacio compartido.

        Args:
            user_id: UUID del usuario que acepta la invitación.
            invitation_code: Código de invitación a aceptar.

        Returns:
            La relación de pareja activada.

        Raises:
            NotFoundException: Si el código de invitación no es válido.
            ConflictException: Si la invitación ya fue usada o el usuario ya tiene pareja.
            ValidationException: Si el usuario intenta aceptar su propia invitación.
        """
        couple = await self.couple_repository.get_by_invitation_code(invitation_code)
        if couple is None:
            raise NotFoundException("Código de invitación no válido.")

        if couple.status != CoupleStatus.PENDING:
            raise ConflictException("Esta invitación ya no está disponible.")

        if couple.partner_one_id == user_id:
            raise ValidationException("No puedes aceptar tu propia invitación.")

        existing = await self.couple_repository.get_active_for_user(user_id)
        if existing is not None:
            raise ConflictException(
                "Ya tienes una relación activa o una invitación pendiente."
            )

        couple.partner_two_id = user_id
        couple.status = CoupleStatus.ACCEPTED

        await self.session.commit()
        return couple
