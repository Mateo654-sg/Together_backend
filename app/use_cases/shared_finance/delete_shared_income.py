"""
Use Case: DeleteSharedIncome.

Elimina lógicamente un ingreso compartido.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.shared_income_repository import SharedIncomeRepository


class DeleteSharedIncomeUseCase:
    """Use Case: DeleteSharedIncome.

    Elimina lógicamente un ingreso compartido de la pareja.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.income_repository = SharedIncomeRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID, income_id: uuid.UUID) -> None:
        """Elimina lógicamente un ingreso compartido.

        Args:
            user_id: UUID del usuario que solicita la eliminación.
            income_id: UUID del ingreso a eliminar.

        Raises:
            ConflictException: Si el usuario no tiene pareja vinculada.
            NotFoundException: Si el ingreso no existe.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        income = await self.income_repository.get_by_couple_and_id(couple.id, income_id)
        if income is None:
            raise NotFoundException("Ingreso compartido no encontrado.")

        await self.income_repository.soft_delete(income)
        await self.session.commit()
