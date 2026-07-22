"""
Use Case: AIScore (FR-105).

Calcula el Score Financiero de la pareja (0-100).
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AIScoreResponse
from app.services.ai.service import AIService


class AIScoreUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)

    async def execute(self, user_id: uuid.UUID) -> AIScoreResponse:
        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)

        score = 50
        factors = []

        if total_income > 0:
            savings_rate = float((total_income - total_expense) / total_income * 100)
            if savings_rate >= 30:
                score += 25
                factors.append({"name": "Ahorro", "value": 25, "max": 25, "status": "Excellent"})
            elif savings_rate >= 20:
                score += 18
                factors.append({"name": "Ahorro", "value": 18, "max": 25, "status": "Good"})
            elif savings_rate >= 10:
                score += 10
                factors.append({"name": "Ahorro", "value": 10, "max": 25, "status": "Fair"})
            else:
                factors.append({"name": "Ahorro", "value": 0, "max": 25, "status": "Poor"})
        else:
            factors.append({"name": "Ahorro", "value": 0, "max": 25, "status": "No data"})

        if len(expenses) > 0:
            score += 15
            factors.append({"name": "Actividad", "value": 15, "max": 15, "status": "Good"})
        else:
            factors.append({"name": "Actividad", "value": 0, "max": 15, "status": "No data"})

        score += 10
        factors.append({"name": "Constancia", "value": 10, "max": 10, "status": "Good"})

        if score >= 80:
            grade = "Excellent"
        elif score >= 60:
            grade = "Good"
        elif score >= 40:
            grade = "Fair"
        else:
            grade = "Poor"

        recommendations = []
        if total_income > 0:
            savings_rate = float((total_income - total_expense) / total_income * 100)
            if savings_rate < 20:
                recommendations.append("Intenta ahorrar al menos el 20% de tus ingresos.")
        if not recommendations:
            recommendations.append("Continúa con el excelente manejo de tus finanzas.")

        return AIScoreResponse(
            score=min(score, 100),
            grade=grade,
            factors=factors,
            recommendations=recommendations,
        )
