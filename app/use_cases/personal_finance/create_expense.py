"""
Use Case: CreateExpense (FR-020).

Registra un gasto personal nuevo.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.personal_expense import PersonalExpense
from app.repositories.expense_tag_repository import ExpenseTagRepository
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.schemas.personal_finance import CreateExpenseRequest


class CreateExpenseUseCase:
    """Use Case: CreateExpense (FR-020).

    Registra un gasto personal nuevo.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalExpenseRepository(session)
        self.category_repository = PersonalCategoryRepository(session)
        self.tag_repository = ExpenseTagRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateExpenseRequest
    ) -> PersonalExpense:
        """Crea un nuevo gasto personal.

        Args:
            user_id: UUID del usuario propietario.
            data: Datos del gasto a crear (amount, description, category_id, etc.).

        Returns:
            El gasto personal creado.

        Raises:
            ValidationException: Si la categoría o alguna etiqueta no existe.
        """
        if data.category_id is not None:
            category = await self.category_repository.get_by_user_and_id(
                user_id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")

        tags = []
        for tag_id in data.tag_ids:
            tag = await self.tag_repository.get_by_user_and_id(user_id, tag_id)
            if tag is None:
                raise ValidationException("Una de las etiquetas especificadas no existe.")
            tags.append(tag)

        expense = PersonalExpense(
            user_id=user_id,
            category_id=data.category_id,
            amount=data.amount,
            description=data.description.strip(),
            notes=data.notes,
            payment_method=data.payment_method,
            location=data.location,
            expense_date=data.expense_date,
            tags=tags,
        )
        await self.repository.create(expense)
        await self.session.commit()
        return expense
