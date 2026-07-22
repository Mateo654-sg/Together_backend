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
    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID) -> Couple:
        existing = await self.couple_repository.get_active_for_user(user_id)
        if existing is not None:
            raise ConflictException(
                "Ya tienes una relación activa o una invitación pendiente."
            )

        code = await self._generate_unique_code()

        couple = Couple(partner_one_id=user_id, invitation_code=code)
        await self.couple_repository.create(couple)
        await self.session.commit()
        await self.couple_repository.refresh(couple)
        return couple

    async def _generate_unique_code(self) -> str:
        for _ in range(MAX_CODE_GENERATION_ATTEMPTS):
            code = generate_invitation_code()
            if not await self.couple_repository.code_exists(code):
                return code
        raise RuntimeError("No se pudo generar un código de invitación único.")
