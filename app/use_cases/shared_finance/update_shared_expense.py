"""
Use Case: UpdateSharedExpense (FR-053).

Edita un gasto compartido existente.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.shared_category_repository import SharedCategoryRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository
from app.schemas.shared_finance import UpdateSharedExpenseRequest

if TYPE_CHECKING:
    from app.models.shared_expense import SharedExpense


class UpdateSharedExpenseUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repository = SharedExpenseRepository(session)
        self.category_repository = SharedCategoryRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self, user_id: uuid.UUID, expense_id: uuid.UUID, data: UpdateSharedExpenseRequest
    ) -> "SharedExpense":
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        expense = await self.expense_repository.get_by_couple_and_id(
            couple.id, expense_id
        )
        if expense is None:
            raise NotFoundException("Gasto compartido no encontrado.")

        if data.category_id is not None:
            category = await self.category_repository.get_by_couple_and_id(
                couple.id, data.category_id
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
        if data.split_type is not None:
            expense.split_type = data.split_type
        if data.split_details is not None:
            expense.split_details = data.split_details
        if data.expense_date is not None:
            expense.expense_date = data.expense_date

        await self.session.commit()
        await self.expense_repository.refresh(expense)
        return expense
