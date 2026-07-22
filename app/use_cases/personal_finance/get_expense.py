"""
Use Case: GetExpense (FR-039 — visualizar un gasto específico).

Obtiene un gasto personal por ID, validando que pertenezca al usuario.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.personal_expense import PersonalExpense
from app.repositories.personal_expense_repository import PersonalExpenseRepository


class GetExpenseUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalExpenseRepository(session)

    async def execute(
        self, user_id: uuid.UUID, expense_id: uuid.UUID
    ) -> PersonalExpense:
        expense = await self.repository.get_by_user_and_id(user_id, expense_id)
        if expense is None:
            raise NotFoundException("Gasto no encontrado.")
        return expense
