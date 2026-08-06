"""
Use Case: AIInsights (FR-098, FR-099).

Genera insights automáticos sobre las finanzas del usuario basados en datos reales.
"""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AIInsightsResponse
from app.services.ai.service import AIService


class AIInsightsUseCase:
    """Use Case: AIInsights (FR-098, FR-099).

    Genera insights financieros automáticos a partir de los datos reales del
    usuario: evolución de gastos, categorías más costosas y progreso de metas.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)
        self.goal_repo = GoalRepository(session)
        self.couple_repo = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID) -> AIInsightsResponse:
        """Genera insights financieros automáticos.

        Args:
            user_id: UUID del usuario.

        Returns:
            AIInsightsResponse con la lista de insights y período analizado.
        """
        question = "Genera insights automáticos sobre mis finanzas de esta semana."
        await self.ai_service.chat(user_id, question, endpoint="insights")

        total_income = await self.income_repo.get_total_by_user(user_id)
        total_expense = await self.expense_repo.get_total_by_user(user_id)
        top_categories = await self.expense_repo.get_category_totals(user_id, limit=1)

        insights: list[dict] = []

        if total_income == 0 and total_expense == 0:
            insights.append(
                {
                    "type": "info",
                    "title": "Empieza a registrar tus finanzas",
                    "description": (
                        "Aún no tienes gastos ni ingresos registrados. Registra tu primer "
                        "movimiento para recibir recomendaciones personalizadas."
                    ),
                    "impact": "info",
                }
            )
            return AIInsightsResponse(insights=insights, period="Acumulado")

        insights.append(
            {
                "type": "info",
                "title": "Resumen de tus finanzas",
                "description": (
                    f"Ingresos: {total_income:,.0f} · Gastos: {total_expense:,.0f} · "
                    f"Saldo: {total_income - total_expense:,.0f}."
                ),
                "impact": "info",
            }
        )

        if total_income > 0 and total_expense > total_income * Decimal("0.7"):
            insights.append(
                {
                    "type": "warning",
                    "title": "Gastos cercanos a tus ingresos",
                    "description": (
                        f"Has gastado {total_expense:,.0f} frente a ingresos de "
                        f"{total_income:,.0f} ({int(total_expense * 100 / total_income)}% "
                        f"de tus ingresos). Considera ajustar tus gastos."
                    ),
                    "impact": "negative",
                }
            )

        if top_categories:
            name, total = top_categories[0]
            insights.append(
                {
                    "type": "saving",
                    "title": f"Gasto principal en {name}",
                    "description": (
                        f"{name} es tu mayor categoría de gasto, con {total:,.0f} acumulados. "
                        f"Revisarla puede liberar presupuesto."
                    ),
                    "impact": "info",
                }
            )

        couple = await self.couple_repo.get_active_for_user(user_id)
        if couple is not None and couple.status == CoupleStatus.ACCEPTED:
            goals_stats = await self.goal_repo.get_statistics(couple.id)
        else:
            goals_stats = await self.goal_repo.get_statistics_for_user(user_id)

        active_goals = goals_stats.get("active_goals", 0) or 0
        if active_goals:
            total_target = goals_stats.get("total_target") or 0
            total_saved = goals_stats.get("total_saved") or 0
            progress = int(total_saved * 100 / total_target) if total_target > 0 else 0
            insights.append(
                {
                    "type": "goal",
                    "title": "Progreso en metas",
                    "description": (
                        f"Tienes {active_goals} meta(s) activa(s) con un progreso promedio "
                        f"del {progress}%. ¡Sigue así!"
                    ),
                    "impact": "positive",
                }
            )

        return AIInsightsResponse(
            insights=insights,
            period="Acumulado",
        )
