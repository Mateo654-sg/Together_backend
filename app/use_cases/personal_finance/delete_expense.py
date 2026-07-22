"""
Use Case: DeleteExpense (FR-023).

Elimina lógicamente (soft delete) un gasto personal.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.personal_expense_repository import PersonalExpenseRepository


class DeleteExpenseUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalExpenseRepository(session)

    async def execute(self, user_id: uuid.UUID, expense_id: uuid.UUID) -> None:
        expense = await self.repository.get_by_user_and_id(user_id, expense_id)
        if expense is None:
            raise NotFoundException("Gasto no encontrado.")

        await self.repository.soft_delete(expense)
        await self.session.commit()
