"""
Use Case: DeleteSharedExpense (FR-054).

Elimina lógicamente un gasto compartido y cancela la deuda asociada.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.couple import CoupleStatus
from app.models.debt import DebtStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.debt_repository import DebtRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository


class DeleteSharedExpenseUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repository = SharedExpenseRepository(session)
        self.debt_repository = DebtRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID, expense_id: uuid.UUID) -> None:
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        expense = await self.expense_repository.get_by_couple_and_id(
            couple.id, expense_id
        )
        if expense is None:
            raise NotFoundException("Gasto compartido no encontrado.")

        # Cancel associated debts
        from app.models.debt import Debt
        from sqlalchemy import select

        stmt = select(Debt).where(
            Debt.shared_expense_id == expense_id,
            Debt.status == DebtStatus.PENDING,
            Debt.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        for debt in result.scalars().all():
            debt.status = DebtStatus.CANCELLED

        await self.expense_repository.soft_delete(expense)
        await self.session.commit()
