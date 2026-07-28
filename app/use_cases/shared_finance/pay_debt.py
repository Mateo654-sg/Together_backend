"""
Use Case: PayDebt (FR-055, FR-058, FR-059).

Marca una deuda como pagada.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.debt import Debt, DebtStatus
from app.repositories.debt_repository import DebtRepository


class PayDebtUseCase:
    """Use Case: PayDebt (FR-055, FR-058, FR-059).

    Marca una deuda como pagada. Solo el deudor puede realizar esta acción.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.debt_repository = DebtRepository(session)

    async def execute(self, user_id: uuid.UUID, debt_id: uuid.UUID) -> Debt:
        """Marca una deuda como pagada.

        Args:
            user_id: UUID del usuario deudor.
            debt_id: UUID de la deuda a pagar.

        Returns:
            La deuda con el estado actualizado a PAID.

        Raises:
            NotFoundException: Si la deuda no existe.
            ValidationException: Si el usuario no es el deudor o la deuda no está pendiente.
        """
        debt = await self.debt_repository.get_by_id(debt_id)
        if debt is None:
            raise NotFoundException("Deuda no encontrada.")

        # Only the debtor can mark as paid
        if debt.debtor_id != user_id:
            raise ValidationException(
                "Solo el deudor puede marcar esta deuda como pagada."
            )

        if debt.status != DebtStatus.PENDING:
            raise ValidationException("Esta deuda ya no está pendiente.")

        debt.status = DebtStatus.PAID
        await self.session.commit()
        return debt
