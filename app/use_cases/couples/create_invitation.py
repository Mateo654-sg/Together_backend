"""
Use Case: CreateInvitation (FR-011, FR-012).

Cada usuario tendrá un código único de invitación y podrá enviar
una invitación para vincular pareja.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.couple import Couple
from app.repositories.couple_repository import CoupleRepository
from app.utils.codes import generate_invitation_code

MAX_CODE_GENERATION_ATTEMPTS = 5


class CreateInvitationUseCase:
    """Use Case: CreateInvitation (FR-011, FR-012).

    Crea un código único de invitación para vincular pareja.
    El código es alfanumérico de 6 caracteres.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID) -> Couple:
        """Crea una nueva invitación de pareja para el usuario.

        Args:
            user_id: UUID del usuario que crea la invitación.

        Returns:
            La relación de pareja con el código de invitación.

        Raises:
            ConflictException: Si el usuario ya tiene una relación activa o pendiente.
            RuntimeError: Si no se pudo generar un código único después de 5 intentos.
        """
        existing = await self.couple_repository.get_active_for_user(user_id)
        if existing is not None:
            raise ConflictException(
                "Ya tienes una relación activa o una invitación pendiente."
            )

        code = await self._generate_unique_code()

        couple = Couple(partner_one_id=user_id, invitation_code=code)
        await self.couple_repository.create(couple)
        await self.session.commit()
        return couple

    async def _generate_unique_code(self) -> str:
        for _ in range(MAX_CODE_GENERATION_ATTEMPTS):
            code = generate_invitation_code()
            if not await self.couple_repository.code_exists(code):
                return code
        raise RuntimeError("No se pudo generar un código de invitación único.")
