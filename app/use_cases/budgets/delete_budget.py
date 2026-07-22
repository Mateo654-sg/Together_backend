"""
Use Case: DeleteBudget.

Elimina (soft delete) un presupuesto existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.budget_repository import BudgetRepository


class DeleteBudgetUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.budget_repository = BudgetRepository(session)

    async def execute(self, user_id: uuid.UUID, budget_id: uuid.UUID) -> None:
        budget = await self.budget_repository.get_by_user_and_id(user_id, budget_id)
        if budget is None:
            raise NotFoundException("Presupuesto no encontrado.")

        await self.budget_repository.soft_delete(budget)
        await self.session.commit()
