"""
Use Case: CreateIncome (FR-019).

Registra un ingreso personal nuevo.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.personal_income import PersonalIncome
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.personal_finance import CreateIncomeRequest


class CreateIncomeUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalIncomeRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateIncomeRequest
    ) -> PersonalIncome:
        if data.category_id is not None:
            category = await self.category_repository.get_by_user_and_id(
                user_id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")

        income = PersonalIncome(
            user_id=user_id,
            category_id=data.category_id,
            amount=data.amount,
            description=data.description.strip(),
            notes=data.notes,
            income_date=data.income_date,
        )
        await self.repository.create(income)
        await self.session.commit()
        await self.repository.refresh(income)
        return income
