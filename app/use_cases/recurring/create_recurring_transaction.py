"""
Use Case: CreateRecurringTransaction (FR-033).

Crea un movimiento recurrente automático.
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.recurring_transaction import RecurringTransaction
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.repositories.recurring_transaction_repository import RecurringTransactionRepository
from app.schemas.recurring_transaction import CreateRecurringTransactionRequest


class CreateRecurringTransactionUseCase:
    """Use Case: CreateRecurringTransaction (FR-033).

    Crea un movimiento recurrente automático.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RecurringTransactionRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateRecurringTransactionRequest
    ) -> RecurringTransaction:
        """Crea un movimiento recurrente.

        Args:
            user_id: UUID del usuario propietario.
            data: Datos de la recurrencia (type, frequency, amount, etc.).

        Returns:
            La recurrencia creada.

        Raises:
            ValidationException: Si la categoría especificada no existe.
        """
        if data.category_id is not None:
            category = await self.category_repository.get_by_user_and_id(
                user_id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")

        base_date = data.next_execution or date.today()
        recurrence = RecurringTransaction(
            user_id=user_id,
            category_id=data.category_id,
            type=data.type,
            frequency=data.frequency,
            amount=data.amount,
            description=data.description.strip(),
            next_execution=base_date,
        )
        await self.repository.create(recurrence)
        await self.session.commit()
        return recurrence
