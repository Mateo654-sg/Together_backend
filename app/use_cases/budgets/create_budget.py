"""
Use Case: CreateBudget (FR-073, FR-074, FR-075, FR-076).

Crea un nuevo presupuesto para el usuario.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ValidationException
from app.models.budget import Budget
from app.repositories.budget_repository import BudgetRepository
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.schemas.budget import CreateBudgetRequest


class CreateBudgetUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.budget_repository = BudgetRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(self, user_id: uuid.UUID, data: CreateBudgetRequest) -> Budget:
        if data.category_id is not None:
            category = await self.category_repository.get_by_user_and_id(
                user_id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")

            existing = await self.budget_repository.get_by_user_category_month(
                user_id, data.category_id, data.month, data.year
            )
            if existing:
                raise ConflictException(
                    "Ya existe un presupuesto para esta categoría en el período indicado."
                )

        budget = Budget(
            user_id=user_id,
            category_id=data.category_id,
            amount=data.amount,
            month=data.month,
            year=data.year,
        )
        await self.budget_repository.create(budget)
        await self.session.commit()
        await self.budget_repository.refresh(budget)
        return budget
