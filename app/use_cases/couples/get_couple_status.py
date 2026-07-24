"""
Use Case: GetCoupleStatus (FR-015).

Retorna el estado de la relación del usuario: sin pareja, pendiente
o vinculada, junto con la información del compañero cuando aplique.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.couple import CoupleStatus
from app.models.user import User
from app.repositories.couple_repository import CoupleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.couple import CoupleResponse, CoupleStatusResponse
from app.schemas.user import UserResponse


class GetCoupleStatusUseCase:
    """Use Case: GetCoupleStatus (FR-015).

    Retorna el estado de la relación del usuario: sin pareja, pendiente
    o vinculada, junto con la información del compañero cuando aplique.
    """

    def __init__(self, session: AsyncSession):
        self.couple_repository = CoupleRepository(session)
        self.user_repository = UserRepository(session)

    async def execute(self, user_id: uuid.UUID) -> CoupleStatusResponse:
        """Obtiene el estado de la relación de pareja del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            CoupleStatusResponse con el estado, datos de la pareja y del partner.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)

        if couple is None:
            return CoupleStatusResponse(status="none")

        partner_response: UserResponse | None = None
        if couple.status == CoupleStatus.ACCEPTED:
            partner_id = (
                couple.partner_two_id
                if couple.partner_one_id == user_id
                else couple.partner_one_id
            )
            partner: User | None = await self.user_repository.get_by_id(partner_id)
            if partner is not None:
                partner_response = UserResponse.model_validate(partner)

        return CoupleStatusResponse(
            status=couple.status.value,
            couple=CoupleResponse.model_validate(couple),
            partner=partner_response,
        )
