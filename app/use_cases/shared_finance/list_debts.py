"""
Use Case: ListDebts (FR-051).

Lista las deudas pendientes del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.debt import Debt
from app.repositories.debt_repository import DebtRepository


class ListDebtsUseCase:
    """Use Case: ListDebts (FR-051).

    Lista las deudas pendientes del usuario.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.debt_repository = DebtRepository(session)

    async def execute(self, user_id: uuid.UUID) -> list[Debt]:
        """Lista todas las deudas pendientes donde el usuario es deudor.

        Args:
            user_id: UUID del usuario deudor.

        Returns:
            Lista de deudas pendientes.
        """
        return await self.debt_repository.list_pending_for_user(user_id)
