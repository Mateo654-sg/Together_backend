"""
Use Case: AIPredictions (FR-103, FR-104).

Genera predicciones de ahorro y cumplimiento de metas.

Las predicciones matemáticas las calcula el Financial Rules Engine.
La IA únicamente interpreta los resultados.
"""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.financial_engine.predictions import (
    balance_forecast,
    cash_flow_forecast,
    goal_completion_forecast,
    savings_forecast,
)
from app.models.goal import GoalStatus
from app.repositories.goal_repository import GoalRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AIPredictionRequest, AIPredictionResponse
from app.services.ai.service import AIService


class AIPredictionsUseCase:
    """Use Case: AIPredictions (FR-103, FR-104).

    Genera predicciones financieras calculadas por el Financial Rules Engine.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)
        self.goal_repo = GoalRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: AIPredictionRequest
    ) -> AIPredictionResponse:
        """Genera predicciones financieras con cálculos del motor.

        Args:
            user_id: UUID del usuario.
            data: Datos de la predicción (prediction_type, months_ahead).

        Returns:
            AIPredictionResponse con predicciones, confianza y recomendaciones.
        """
        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)

        if data.prediction_type == "goal_completion":
            predictions = await self._build_goal_completion(user_id)
        elif data.prediction_type == "cash_flow":
            predictions = cash_flow_forecast(total_income, total_expense, data.months_ahead)
        elif data.prediction_type == "balance":
            balance = total_income - total_expense
            result = balance_forecast(balance, total_income, total_expense)
            predictions = [result]
        else:
            predictions = savings_forecast(total_income, total_expense, data.months_ahead)

        if not predictions:
            predictions = [
                {
                    "month": 1,
                    "predicted_savings": 0,
                    "confidence": 0.0,
                    "message": "Sin datos suficientes para predecir.",
                }
            ]

        confidence = float(max(item.get("confidence", 0) for item in predictions))

        question = self._build_prompt(data)
        await self.ai_service.chat(user_id, question, endpoint="predictions")

        return AIPredictionResponse(
            prediction_type=data.prediction_type,
            predictions=predictions,
            confidence=confidence,
            recommendations=self._build_recommendations(data, predictions),
        )

    async def _build_goal_completion(self, user_id: uuid.UUID) -> list[dict]:
        goals, _ = await self.goal_repo.list_by_user(
            user_id, status=GoalStatus.ACTIVE
        )
        goal = next((g for g in goals if g.target_amount > 0), None)
        if goal is None:
            return []

        savings = max(
            await self._monthly_savings(user_id),
            Decimal("0"),
        )
        forecast = goal_completion_forecast(
            goal.current_amount, goal.target_amount, savings
        )
        return [
            {
                "goal_id": str(goal.id),
                "title": goal.title,
                "months_remaining": forecast["months_remaining"],
                "estimated_date": forecast["estimated_date"],
                "confidence": 0.85,
            }
        ]

    async def _monthly_savings(self, user_id: uuid.UUID) -> Decimal:
        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)
        return total_income - total_expense

    @staticmethod
    def _build_prompt(data: AIPredictionRequest) -> str:
        prompts = {
            "savings": f"Predice mi ahorro para los próximos {data.months_ahead} meses basado en mis tendencias actuales.",
            "goal_completion": "Predice cuándo cumpliré mis metas financieras actuales.",
            "cash_flow": f"Predice mi flujo de caja para los próximos {data.months_ahead} meses.",
            "balance": "Predice mi saldo para fin de mes.",
        }
        return prompts.get(
            data.prediction_type, f"Genera predicciones: {data.prediction_type}"
        )

    @staticmethod
    def _build_recommendations(data: AIPredictionRequest, predictions: list[dict]) -> list[str]:
        recommendations = [
            "Mantén tu ritmo de ahorro actual.",
            "Considera automatizar transferencias a tu fondo de ahorro.",
        ]
        if data.prediction_type == "goal_completion" and predictions:
            forecast = predictions[0]
            months = forecast.get("months_remaining")
            if months is not None and months >= 0:
                recommendations.insert(
                    0,
                    f"Se estima cumplir la meta en {months} meses al ritmo actual.",
                )
        return recommendations
