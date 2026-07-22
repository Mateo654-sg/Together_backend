"""
Use Case: AIFinancialHealth.

Evalúa la salud financiera del usuario.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AIFinancialHealthResponse
from app.services.ai.service import AIService


class AIFinancialHealthUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)

    async def execute(self, user_id: uuid.UUID) -> AIFinancialHealthResponse:
        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)

        balance = total_income - total_expense
        savings_rate = float(balance / total_income * 100) if total_income > 0 else 0

        if savings_rate >= 30:
            status = "Excellent"
            score = 90
        elif savings_rate >= 20:
            status = "Good"
            score = 75
        elif savings_rate >= 10:
            status = "Fair"
            score = 55
        else:
            status = "Critical"
            score = 30

        indicators = {
            "liquidity": float(balance),
            "savings_rate": savings_rate,
            "expense_ratio": float(total_expense / total_income * 100) if total_income > 0 else 100,
            "stability": "Stable" if total_income > 0 else "No income",
        }

        recommendations = []
        if savings_rate < 20:
            recommendations.append("Tu tasa de ahorro es baja. Intenta reducir gastos hormiga.")
        if total_expense > total_income and total_income > 0:
            recommendations.append("Estás gastando más de lo que ingresas. Revisa tus gastos fijos.")
        if not recommendations:
            recommendations.append("Tu salud financiera es buena. Mantén tus hábitos actuales.")

        return AIFinancialHealthResponse(
            status=status,
            score=score,
            indicators=indicators,
            recommendations=recommendations,
        )
