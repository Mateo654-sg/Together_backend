"""
Use Case: UnlinkCouple (FR-018).

Desvincula la pareja. Se marca como 'separated' y se aplica Soft Delete,
de modo que ambos usuarios quedan libres para crear/aceptar una nueva
relación (NFR-018: nunca DELETE físico).
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository


class UnlinkCoupleUseCase:
    """Use Case: UnlinkCouple (FR-018).

    Desvincula la pareja. Se marca como 'separated' y se aplica Soft Delete,
    de modo que ambos usuarios quedan libres para crear/aceptar una nueva
    relación (NFR-018: nunca DELETE físico).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID) -> None:
        """Desvincula la pareja del usuario.

        Args:
            user_id: UUID del usuario que solicita la desvinculación.

        Raises:
            NotFoundException: Si el usuario no tiene una pareja vinculada.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None:
            raise NotFoundException("No tienes una pareja vinculada.")

        couple.status = CoupleStatus.SEPARATED
        await self.couple_repository.soft_delete(couple)
        await self.session.commit()
