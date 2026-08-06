"""
Use Case: AIRecommendations (FR-106, FR-108).

Genera recomendaciones personalizadas de ahorro basadas en los datos reales
del usuario.
"""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AIRecommendationsResponse
from app.services.ai.service import AIService


class AIRecommendationsUseCase:
    """Use Case: AIRecommendations (FR-106, FR-108).

    Genera recomendaciones personalizadas de ahorro con potencial calculado
    a partir de los gastos e ingresos reales del usuario.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)

    async def execute(self, user_id: uuid.UUID) -> AIRecommendationsResponse:
        """Genera recomendaciones personalizadas de ahorro.

        Args:
            user_id: UUID del usuario.

        Returns:
            AIRecommendationsResponse con recomendaciones y ahorro potencial.
        """
        question = "Genera recomendaciones personalizadas para mejorar mis finanzas."
        await self.ai_service.chat(user_id, question, endpoint="recommendations")

        total_income = await self.income_repo.get_total_by_user(user_id)
        total_expense = await self.expense_repo.get_total_by_user(user_id)
        top_categories = await self.expense_repo.get_category_totals(user_id, limit=3)

        potential_savings = Decimal("0")
        if total_income > 0:
            potential_savings = (total_income - total_expense) * Decimal("0.1")

        recommendations = []

        if top_categories:
            top_name, top_total = top_categories[0]
            half = (top_total / 2).quantize(Decimal("1"))
            recommendations.append(
                {
                    "title": f"Revisar gastos en {top_name}",
                    "description": (
                        f"Tu mayor categoría de gasto es {top_name} "
                        f"({top_total:,.0f}). Reducirla a la mitad podría ahorrarte "
                        f"~{half:,.0f} en el período."
                    ),
                    "potential_saving": half,
                    "difficulty": "easy",
                }
            )

        if total_income > 0:
            ten_percent = (total_income * Decimal("0.1")).quantize(Decimal("1"))
            recommendations.append(
                {
                    "title": "Automatizar ahorros",
                    "description": (
                        f"Configura transferencias automáticas para ahorrar el 10% "
                        f"de tus ingresos (~{ten_percent:,.0f})."
                    ),
                    "potential_saving": ten_percent,
                    "difficulty": "easy",
                }
            )

        recommendations.append(
            {
                "title": "Revisar suscripciones",
                "description": (
                    "Revisa los pagos recurrentes y cancela servicios que no usas "
                    "regularmente para liberar presupuesto."
                ),
                "potential_saving": 0,
                "difficulty": "medium",
            }
        )

        return AIRecommendationsResponse(
            recommendations=recommendations,
            potential_savings=potential_savings,
        )
