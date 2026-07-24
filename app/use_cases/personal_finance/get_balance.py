"""
Use Case: GetPersonalBalance (FR-040).

Consulta el saldo personal del usuario: total ingresos - total gastos.
"""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.personal_expense_repository import PersonalExpenseRepository


class GetPersonalBalanceUseCase:
    """Use Case: GetPersonalBalance (FR-040).

    Consulta el saldo personal del usuario: total ingresos - total gastos.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repository = PersonalExpenseRepository(session)

    async def execute(self, user_id: uuid.UUID) -> Decimal:
        """Calcula el saldo personal del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            Saldo personal como Decimal (ingresos - gastos).
        """
        return await self.expense_repository.get_balance(user_id)
