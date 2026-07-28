"""
Use Case: CreateSharedIncome (FR-042).

Registra un ingreso compartido entre la pareja.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.couple import CoupleStatus
from app.models.shared_income import SharedIncome
from app.repositories.couple_repository import CoupleRepository
from app.repositories.shared_income_repository import SharedIncomeRepository
from app.schemas.shared_finance import CreateSharedIncomeRequest


class CreateSharedIncomeUseCase:
    """Use Case: CreateSharedIncome (FR-042).

    Registra un ingreso compartido entre la pareja.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.income_repository = SharedIncomeRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateSharedIncomeRequest
    ) -> SharedIncome:
        """Crea un ingreso compartido para la pareja.

        Args:
            user_id: UUID del usuario que recibe el ingreso.
            data: Datos del ingreso compartido.

        Returns:
            El ingreso compartido creado.

        Raises:
            ConflictException: Si el usuario no tiene pareja vinculada.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        income = SharedIncome(
            couple_id=couple.id,
            received_by=user_id,
            amount=data.amount,
            description=data.description.strip(),
            notes=data.notes,
            income_date=data.income_date,
        )
        await self.income_repository.create(income)
        await self.session.commit()
        return income
