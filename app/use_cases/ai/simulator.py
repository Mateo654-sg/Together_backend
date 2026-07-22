"""
Use Case: AISimulator.

Simula escenarios financieros "¿Qué pasaría si...?"
"""
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AISimulatorRequest, AISimulatorResponse
from app.services.ai.service import AIService


class AISimulatorUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: AISimulatorRequest
    ) -> AISimulatorResponse:
        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)

        monthly_savings = total_income - total_expense

        current_projection = {
            "monthly_savings": float(monthly_savings),
            "total_savings": float(monthly_savings * data.months),
        }

        extra = data.monthly_amount or Decimal("0")
        simulated_monthly = monthly_savings + extra

        simulated_projection = {
            "monthly_savings": float(simulated_monthly),
            "total_savings": float(simulated_monthly * data.months),
        }

        difference = {
            "monthly_difference": float(extra),
            "total_difference": float(extra * data.months),
        }

        recommendation = f"Si ahorraras ${extra:,.0f} adicionales mensuales, en {data.months} meses tendrías ${simulated_projection['total_savings']:,.0f} COP."

        return AISimulatorResponse(
            scenario=data.scenario,
            current_projection=current_projection,
            simulated_projection=simulated_projection,
            difference=difference,
            recommendation=recommendation,
        )
