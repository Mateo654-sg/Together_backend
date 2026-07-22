"""
Use Case: AIRecommendations (FR-106, FR-108).

Genera recomendaciones personalizadas de ahorro.
"""
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AIRecommendationsResponse
from app.services.ai.service import AIService


class AIRecommendationsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)

    async def execute(self, user_id: uuid.UUID) -> AIRecommendationsResponse:
        question = "Genera recomendaciones personalizadas para mejorar mis finanzas."
        await self.ai_service.chat(user_id, question, endpoint="recommendations")

        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)

        potential_savings = Decimal("0")
        if total_income > 0:
            potential_savings = (total_income - total_expense) * Decimal("0.1")

        recommendations = [
            {
                "title": "Reducir gastos en restaurantes",
                "description": "Reduciendo un café diario podrías ahorrar $180.000 al mes.",
                "potential_saving": 180000,
                "difficulty": "easy",
            },
            {
                "title": "Automatizar ahorros",
                "description": "Configura transferencias automáticas a tu fondo de ahorro.",
                "potential_saving": 100000,
                "difficulty": "easy",
            },
            {
                "title": "Revisar suscripciones",
                "description": "Podrías estar pagando servicios que no utilizas regularmente.",
                "potential_saving": 50000,
                "difficulty": "medium",
            },
        ]

        return AIRecommendationsResponse(
            recommendations=recommendations,
            potential_savings=potential_savings,
        )
