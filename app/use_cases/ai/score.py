"""
Use Case: AIScore (FR-105).

Calcula el Score Financiero del usuario (0-100).

Todo el cálculo lo realiza el Financial Rules Engine (Motor 12).
La IA únicamente interpreta los resultados.
"""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.financial_engine import (
    debt_score,
    expense_ratio,
    financial_score,
    goals_component,
    liquidity_ratio,
    monthly_average,
    net_cash_flow,
    savings_rate,
    score_grade_en,
)
from app.models.goal import GoalStatus
from app.repositories.debt_repository import DebtRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AIScoreResponse


class AIScoreUseCase:
    """Use Case: AIScore (FR-105).

    Calcula el Score Financiero del usuario (0-100) delegando el
    cálculo al Financial Rules Engine.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)
        self.debt_repo = DebtRepository(session)
        self.goal_repo = GoalRepository(session)

    async def execute(self, user_id: uuid.UUID) -> AIScoreResponse:
        """Calcula el score financiero del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            AIScoreResponse con score, grade, factors y recommendations.
        """
        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)

        saving_rate = savings_rate(total_income, total_expense)
        cash_flow = net_cash_flow(total_income, total_expense)
        budget_consumption = expense_ratio(total_expense, total_income)
        average_monthly = monthly_average(total_expense, self._months_span(expenses))

        balance = cash_flow
        liquidity = liquidity_ratio(balance, average_monthly)

        debts = await self.debt_repo.list_pending_for_user(user_id)
        total_debt = sum(d.amount for d in debts)
        debt_component = debt_score(len(debts), total_debt)

        goals, _ = await self.goal_repo.list_by_user(
            user_id, status=GoalStatus.ACTIVE
        )
        progresses = [
            Decimal(str(g.current_amount)) / Decimal(str(g.target_amount)) * 100
            if g.target_amount > 0
            else Decimal("0")
            for g in goals
        ]
        goals_comp = goals_component(progresses)

        score = financial_score(
            savings_rate=saving_rate,
            budget_consumption=budget_consumption,
            debt=debt_component,
            liquidity=liquidity,
            goals=goals_comp,
            cash_flow=cash_flow,
        )

        factors = [
            {"name": "Saving Rate", "value": int(saving_rate), "max": 100, "weight": 25},
            {
                "name": "Budget Control",
                "value": int(Decimal("100") - budget_consumption),
                "max": 100,
                "weight": 20,
            },
            {"name": "Debt", "value": int(debt_component), "max": 100, "weight": 20},
            {"name": "Liquidity", "value": int(liquidity * 15), "max": 100, "weight": 15},
            {"name": "Goals", "value": int(goals_comp), "max": 100, "weight": 10},
            {"name": "Cash Flow", "value": int(cash_flow), "max": 100, "weight": 10},
        ]

        grade = score_grade_en(score)
        recommendations = self._build_recommendations(saving_rate, total_expense, total_income, goals_comp)

        return AIScoreResponse(
            score=min(int(score), 100),
            grade=grade,
            factors=factors,
            recommendations=recommendations,
        )

    @staticmethod
    def _months_span(expenses) -> int:
        if not expenses:
            return 1
        months = {
            (e.expense_date.year, e.expense_date.month)
            for e in expenses
            if e.expense_date is not None
        }
        return max(len(months), 1)

    @staticmethod
    def _build_recommendations(
        saving_rate: Decimal, total_expense: Decimal, total_income: Decimal, goals_comp: Decimal
    ) -> list[str]:
        recommendations = []
        if total_income > 0 and saving_rate < Decimal("20"):
            recommendations.append("Intenta ahorrar al menos el 20% de tus ingresos.")
        if total_expense > total_income and total_income > 0:
            recommendations.append("Estás gastando más de lo que ingresas. Revisa tus gastos fijos.")
        if goals_comp < Decimal("30"):
            recommendations.append("Tus metas van lentas. Considera aumentar tus aportes.")
        if not recommendations:
            recommendations.append("Continúa con el excelente manejo de tus finanzas.")
        return recommendations
