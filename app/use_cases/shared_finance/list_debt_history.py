"""
Use Case: ListDebtHistory.

Retorna el historial completo de deudas de la pareja.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.couple import CoupleStatus
from app.models.debt import Debt
from app.repositories.couple_repository import CoupleRepository
from app.repositories.debt_repository import DebtRepository


class ListDebtHistoryUseCase:
    """Use Case: ListDebtHistory.

    Retorna el historial completo de deudas de la pareja.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.debt_repository = DebtRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID) -> list[Debt]:
        """Lista el historial completo de deudas de la pareja.

        Args:
            user_id: UUID del usuario.

        Returns:
            Lista de todas las deudas de la pareja (historial).

        Raises:
            ConflictException: Si el usuario no tiene pareja vinculada.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        return await self.debt_repository.list_for_couple(couple.id)
