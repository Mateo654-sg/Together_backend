"""
Use Case: UpdateSharedIncome.

Edita un ingreso compartido existente.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.shared_income_repository import SharedIncomeRepository
from app.schemas.shared_finance import UpdateSharedIncomeRequest


class UpdateSharedIncomeUseCase:
    """Use Case: UpdateSharedIncome.

    Actualiza los campos de un ingreso compartido de la pareja.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.income_repository = SharedIncomeRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        income_id: uuid.UUID,
        data: UpdateSharedIncomeRequest,
    ):
        """Actualiza un ingreso compartido existente.

        Args:
            user_id: UUID del usuario que solicita la edición.
            income_id: UUID del ingreso a actualizar.
            data: Datos a actualizar (parciales).

        Returns:
            El ingreso compartido actualizado.

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

        if data.amount is not None:
            income.amount = data.amount
        if data.description is not None:
            income.description = data.description.strip()
        if data.notes is not None:
            income.notes = data.notes
        if data.income_date is not None:
            income.income_date = data.income_date

        await self.session.commit()
        return income
