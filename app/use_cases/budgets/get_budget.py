"""
Use Case: GetBudget.

Obtiene un presupuesto del usuario con gasto consumido y porcentaje calculados.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import BudgetResponse


class GetBudgetUseCase:
    """Use Case: GetBudget.

    Obtiene un presupuesto verificando la propiedad del usuario y enriquece
    la respuesta con el gasto consumido y el porcentaje.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.budget_repository = BudgetRepository(session)

    async def execute(self, user_id: uuid.UUID, budget_id: uuid.UUID) -> BudgetResponse:
        """Obtiene un presupuesto del usuario con métricas calculadas.

        Args:
            user_id: UUID del usuario propietario.
            budget_id: UUID del presupuesto a consultar.

        Returns:
            BudgetResponse con el presupuesto enriquecido.

        Raises:
            NotFoundException: Si el presupuesto no existe o no pertenece al usuario.
        """
        budget = await self.budget_repository.get_by_user_and_id(user_id, budget_id)
        if budget is None:
            raise NotFoundException("Presupuesto no encontrado.")

        resp = BudgetResponse.model_validate(budget)
        resp.category_name = budget.category.name if budget.category else None
        spent = await self.budget_repository._get_spent_amount(user_id, budget)
        resp.spent = spent
        resp.percentage_consumed = (
            min(float(spent / budget.amount * 100), 100.0)
            if budget.amount > 0
            else 0.0
        )
        return resp
