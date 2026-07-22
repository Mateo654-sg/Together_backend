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
    def __init__(self, session: AsyncSession):
        self.session = session
        self.debt_repository = DebtRepository(session)

    async def execute(self, user_id: uuid.UUID, debt_id: uuid.UUID) -> Debt:
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
        await self.debt_repository.refresh(debt)
        return debt
