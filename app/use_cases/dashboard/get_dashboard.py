"""
Use Case: GetDashboard (FR-079 a FR-088).

Agrega datos de todos los módulos para el dashboard principal.
"""
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository
from app.repositories.shared_income_repository import SharedIncomeRepository
from app.schemas.dashboard import (
    DashboardGoalSummary,
    DashboardRecentActivity,
    DashboardResponse,
    DashboardUpcomingPayment,
)


class GetDashboardUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.personal_expense_repo = PersonalExpenseRepository(session)
        self.personal_income_repo = PersonalIncomeRepository(session)
        self.shared_expense_repo = SharedExpenseRepository(session)
        self.shared_income_repo = SharedIncomeRepository(session)
        self.couple_repository = CoupleRepository(session)
        self.goal_repository = GoalRepository(session)

    async def execute(self, user_id: uuid.UUID) -> DashboardResponse:
        total_income = await self.personal_income_repo.get_total_by_user(user_id)
        total_expense = Decimal("0")
        expenses, _ = await self.personal_expense_repo.list_by_user(
            user_id, page=1, limit=1000
        )
        for exp in expenses:
            total_expense += exp.amount

        balance = total_income - total_expense
        saving = balance

        couple = await self.couple_repository.get_active_for_user(user_id)
        goals_data = []
        if couple and couple.status == CoupleStatus.ACCEPTED:
            goals, _ = await self.goal_repository.list_by_couple(
                couple.id, status=GoalStatus.ACTIVE, limit=5
            )
            for goal in goals:
                progress = (
                    float(goal.current_amount / goal.target_amount * 100)
                    if goal.target_amount > 0
                    else 0.0
                )
                goals_data.append(
                    DashboardGoalSummary(
                        id=goal.id,
                        title=goal.title,
                        target_amount=goal.target_amount,
                        current_amount=goal.current_amount,
                        progress_percentage=min(progress, 100.0),
                        target_date=goal.target_date,
                        status=goal.status.value,
                    )
                )

        recent_activity = self._build_recent_activity(expenses)

        upcoming_payments = self._build_upcoming_payments(expenses)

        statistics = {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(balance),
            "savings_rate": float(saving / total_income * 100) if total_income > 0 else 0.0,
            "transaction_count": len(expenses),
        }

        ai_recommendations = self._generate_recommendations(
            total_income, total_expense, balance, goals_data
        )

        return DashboardResponse(
            balance=balance,
            income=total_income,
            expense=total_expense,
            saving=saving,
            cash_flow=balance,
            goals=goals_data,
            statistics=statistics,
            recent_activity=recent_activity,
            upcoming_payments=upcoming_payments,
            ai_recommendations=ai_recommendations,
        )

    def _build_recent_activity(self, expenses) -> list[DashboardRecentActivity]:
        activities = []
        for exp in expenses[:10]:
            activities.append(
                DashboardRecentActivity(
                    id=exp.id,
                    type="expense",
                    description=exp.description,
                    amount=exp.amount,
                    date=exp.expense_date,
                    category=None,
                )
            )
        return activities

    def _build_upcoming_payments(self, expenses) -> list[DashboardUpcomingPayment]:
        upcoming = []
        today = date.today()
        for exp in expenses:
            if exp.expense_date > today:
                upcoming.append(
                    DashboardUpcomingPayment(
                        id=exp.id,
                        type="expense",
                        description=exp.description,
                        amount=exp.amount,
                        due_date=exp.expense_date,
                        status="pending",
                    )
                )
            if len(upcoming) >= 5:
                break
        return upcoming

    def _generate_recommendations(
        self,
        total_income: Decimal,
        total_expense: Decimal,
        balance: Decimal,
        goals: list[DashboardGoalSummary],
    ) -> list[str]:
        recommendations = []

        if total_income > 0:
            savings_rate = float(balance / total_income * 100)
            if savings_rate < 20:
                recommendations.append(
                    "Tu tasa de ahorro es menor al 20%. Intenta reducir gastos variables."
                )
            elif savings_rate >= 50:
                recommendations.append(
                    "Excelente tasa de ahorro! Considera invertir parte de tus ahorros."
                )

        if total_expense > total_income and total_income > 0:
            recommendations.append(
                "Estás gastando más de lo que ingresa. Revisa tus gastos fijos."
            )

        for goal in goals:
            if goal.target_date and goal.progress_percentage < 30:
                recommendations.append(
                    f"La meta '{goal.title}' va lenta. Considera aumentar tus aportes."
                )

        if not recommendations:
            recommendations.append(
                "Registra más transacciones para obtener recomendaciones personalizadas."
            )

        return recommendations
