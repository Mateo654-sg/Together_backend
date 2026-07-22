"""
Use Case: UpdateIncome (FR-022).

Edita un ingreso personal existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.personal_income import PersonalIncome
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.personal_finance import UpdateIncomeRequest


class UpdateIncomeUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalIncomeRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(
        self, user_id: uuid.UUID, income_id: uuid.UUID, data: UpdateIncomeRequest
    ) -> PersonalIncome:
        income = await self.repository.get_by_user_and_id(user_id, income_id)
        if income is None:
            raise NotFoundException("Ingreso no encontrado.")

        if data.category_id is not None:
            category = await self.category_repository.get_by_user_and_id(
                user_id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")
            income.category_id = data.category_id

        if data.amount is not None:
            income.amount = data.amount
        if data.description is not None:
            income.description = data.description.strip()
        if data.notes is not None:
            income.notes = data.notes
        if data.income_date is not None:
            income.income_date = data.income_date

        await self.session.commit()
        await self.repository.refresh(income)
        return income
