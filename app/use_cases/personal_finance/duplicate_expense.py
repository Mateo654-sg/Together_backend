"""
Use Case: DuplicateExpense (FR-034).

Duplica un gasto existente con la fecha de hoy.
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.personal_expense import PersonalExpense
from app.repositories.personal_expense_repository import PersonalExpenseRepository


class DuplicateExpenseUseCase:
    """Use Case: DuplicateExpense (FR-034).

    Duplica un gasto existente con la fecha de hoy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalExpenseRepository(session)

    async def execute(
        self, user_id: uuid.UUID, expense_id: uuid.UUID
    ) -> PersonalExpense:
        """Duplica un gasto personal con la fecha actual.

        Args:
            user_id: UUID del usuario propietario.
            expense_id: UUID del gasto a duplicar.

        Returns:
            El nuevo gasto duplicado con fecha de hoy.

        Raises:
            NotFoundException: Si el gasto original no existe.
        """
        original = await self.repository.get_by_user_and_id(user_id, expense_id)
        if original is None:
            raise NotFoundException("Gasto no encontrado.")

        duplicate = PersonalExpense(
            user_id=user_id,
            category_id=original.category_id,
            amount=original.amount,
            description=original.description,
            notes=original.notes,
            payment_method=original.payment_method,
            location=original.location,
            expense_date=date.today(),
            is_favorite=False,
        )
        await self.repository.create(duplicate)
        await self.session.commit()
        await self.repository.refresh(duplicate)
        return duplicate
