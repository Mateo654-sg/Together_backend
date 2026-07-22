"""
Use Case: UpdateBudget (FR-073 a FR-076).

Edita un presupuesto existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.budget_repository import BudgetRepository
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.schemas.budget import UpdateBudgetRequest


class UpdateBudgetUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.budget_repository = BudgetRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(
        self, user_id: uuid.UUID, budget_id: uuid.UUID, data: UpdateBudgetRequest
    ):
        budget = await self.budget_repository.get_by_user_and_id(user_id, budget_id)
        if budget is None:
            raise NotFoundException("Presupuesto no encontrado.")

        if data.category_id is not None:
            category = await self.category_repository.get_by_user_and_id(
                user_id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")
            budget.category_id = data.category_id

        if data.amount is not None:
            budget.amount = data.amount
        if data.month is not None:
            budget.month = data.month
        if data.year is not None:
            budget.year = data.year

        await self.session.commit()
        await self.budget_repository.refresh(budget)
        return budget
