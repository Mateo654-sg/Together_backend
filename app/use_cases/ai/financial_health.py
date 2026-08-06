"""
Use Case: AIFinancialHealth.

Evalúa la salud financiera del usuario.

El cálculo lo realiza el Financial Rules Engine (Motor 13).
La IA solo interpreta los resultados.
"""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.financial_engine import (
    expense_ratio,
    financial_score,
    health_status_en,
    liquidity_ratio,
    monthly_average,
    net_cash_flow,
    savings_rate,
)
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AIFinancialHealthResponse


class AIFinancialHealthUseCase:
    """Use Case: AIFinancialHealth.

    Evalúa la salud financiera del usuario con score (0-100),
    indicadores y recomendaciones personalizadas.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)

    async def execute(self, user_id: uuid.UUID) -> AIFinancialHealthResponse:
        """Evalúa la salud financiera del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            AIFinancialHealthResponse con status, score, indicators y recommendations.
        """
        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)

        balance = net_cash_flow(total_income, total_expense)
        saving_rate = savings_rate(total_income, total_expense)
        ratio = expense_ratio(total_expense, total_income)

        average_monthly = monthly_average(
            total_expense, max(len({(e.expense_date.year, e.expense_date.month) for e in expenses if e.expense_date}), 1)
        )
        liquidity = liquidity_ratio(balance, average_monthly)

        score = financial_score(
            savings_rate=saving_rate,
            budget_consumption=ratio,
            debt=Decimal("100"),
            liquidity=liquidity,
            goals=Decimal("0"),
            cash_flow=balance,
        )

        status = health_status_en(score)

        indicators = {
            "liquidity": float(balance),
            "liquidity_ratio": float(liquidity),
            "savings_rate": float(saving_rate),
            "expense_ratio": float(ratio),
            "stability": "Stable" if total_income > 0 else "No income",
        }

        recommendations = []
        if saving_rate < Decimal("20"):
            recommendations.append(
                "Tu tasa de ahorro es baja. Intenta reducir gastos hormiga."
            )
        if total_expense > total_income and total_income > 0:
            recommendations.append(
                "Estás gastando más de lo que ingresas. Revisa tus gastos fijos."
            )
        if not recommendations:
            recommendations.append(
                "Tu salud financiera es buena. Mantén tus hábitos actuales."
            )

        return AIFinancialHealthResponse(
            status=status,
            score=min(int(score), 100),
            indicators=indicators,
            recommendations=recommendations,
        )
