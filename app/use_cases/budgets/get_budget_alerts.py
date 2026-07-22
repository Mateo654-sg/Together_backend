"""
Use Case: GetBudgetAlerts (FR-077, FR-078).

Obtiene alertas de presupuestos que superan los umbrales 80%, 90%, 100%.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import BudgetAlertListResponse, BudgetAlertResponse


class GetBudgetAlertsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.budget_repository = BudgetRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        month: int | None = None,
        year: int | None = None,
    ) -> BudgetAlertListResponse:
        alerts = await self.budget_repository.get_alerts(
            user_id, month=month, year=year
        )

        data = [BudgetAlertResponse(**alert) for alert in alerts]

        return BudgetAlertListResponse(data=data)
