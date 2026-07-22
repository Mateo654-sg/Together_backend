"""
Use Case: ListBudgets.

Lista los presupuestos del usuario con paginación y filtros.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import BudgetListResponse, BudgetResponse


class ListBudgetsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.budget_repository = BudgetRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        month: int | None = None,
        year: int | None = None,
        category_id: uuid.UUID | None = None,
    ) -> BudgetListResponse:
        budgets, total = await self.budget_repository.list_by_user(
            user_id, page=page, limit=limit, month=month, year=year, category_id=category_id
        )

        data = []
        for budget in budgets:
            resp = BudgetResponse.model_validate(budget)
            spent = await self.budget_repository._get_spent_amount(user_id, budget)
            resp.spent = spent
            resp.percentage_consumed = (
                min(float(spent / budget.amount * 100), 100.0) if budget.amount > 0 else 0.0
            )
            data.append(resp)

        return BudgetListResponse(
            data=data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )
