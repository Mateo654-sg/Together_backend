"""
Use Case: UpdateExpense (FR-022).

Edita un gasto personal existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.personal_expense import PersonalExpense
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.schemas.personal_finance import UpdateExpenseRequest


class UpdateExpenseUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalExpenseRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(
        self, user_id: uuid.UUID, expense_id: uuid.UUID, data: UpdateExpenseRequest
    ) -> PersonalExpense:
        expense = await self.repository.get_by_user_and_id(user_id, expense_id)
        if expense is None:
            raise NotFoundException("Gasto no encontrado.")

        if data.category_id is not None:
            category = await self.category_repository.get_by_user_and_id(
                user_id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")
            expense.category_id = data.category_id

        if data.amount is not None:
            expense.amount = data.amount
        if data.description is not None:
            expense.description = data.description.strip()
        if data.notes is not None:
            expense.notes = data.notes
        if data.payment_method is not None:
            expense.payment_method = data.payment_method
        if data.location is not None:
            expense.location = data.location
        if data.expense_date is not None:
            expense.expense_date = data.expense_date
        if data.is_favorite is not None:
            expense.is_favorite = data.is_favorite

        await self.session.commit()
        await self.repository.refresh(expense)
        return expense
