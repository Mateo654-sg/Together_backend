"""
Use Case: UpdateRecurringTransaction (FR-033-Update).

Edita un movimiento recurrente existente.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.recurring_transaction import RecurringTransaction
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.repositories.recurring_transaction_repository import RecurringTransactionRepository
from app.schemas.recurring_transaction import UpdateRecurringTransactionRequest


class UpdateRecurringTransactionUseCase:
    """Use Case: UpdateRecurringTransaction (FR-033-Update)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RecurringTransactionRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        recurring_id: uuid.UUID,
        data: UpdateRecurringTransactionRequest,
    ) -> RecurringTransaction:
        """Edita un movimiento recurrente.

        Args:
            user_id: UUID del usuario propietario.
            recurring_id: UUID de la recurrencia.
            data: Datos a actualizar.

        Returns:
            La recurrencia actualizada.

        Raises:
            NotFoundException: Si la recurrencia no existe.
            ValidationException: Si la categoría especificada no existe.
        """
        recurrence = await self.repository.get_by_user_and_id(user_id, recurring_id)
        if recurrence is None:
            raise NotFoundException("Movimiento recurrente no encontrado.")

        if data.category_id is not None:
            category = await self.category_repository.get_by_user_and_id(
                user_id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")

        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            if field == "description" and value is not None:
                value = value.strip()
            setattr(recurrence, field, value)

        await self.session.commit()
        await self.session.refresh(recurrence)
        return recurrence
