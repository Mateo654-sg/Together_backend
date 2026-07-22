"""
Use Case: GetCoupleDashboard.

Dashboard específico para parejas con datos compartidos.
"""
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository
from app.repositories.shared_income_repository import SharedIncomeRepository
from app.schemas.dashboard import (
    CoupleDashboardResponse,
    DashboardGoalSummary,
    DashboardRecentActivity,
    DashboardUpcomingPayment,
)


class GetCoupleDashboardUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.personal_expense_repo = PersonalExpenseRepository(session)
        self.personal_income_repo = PersonalIncomeRepository(session)
        self.shared_expense_repo = SharedExpenseRepository(session)
        self.shared_income_repo = SharedIncomeRepository(session)
        self.couple_repository = CoupleRepository(session)
        self.goal_repository = GoalRepository(session)

    async def execute(self, user_id: uuid.UUID) -> CoupleDashboardResponse:
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        personal_income = await self.personal_income_repo.get_total_by_user(user_id)
        personal_expenses, _ = await self.personal_expense_repo.list_by_user(
            user_id, page=1, limit=1000
        )
        personal_expense_total = sum(e.amount for e in personal_expenses)

        shared_expenses_total = await self.shared_expense_repo.get_total_by_couple(couple.id)
        shared_income_total = Decimal("0")
        shared_incomes, _ = await self.shared_income_repo.list_by_couple(
            couple.id, page=1, limit=1000
        )
        for inc in shared_incomes:
            shared_income_total += inc.amount

        personal_balance = personal_income - personal_expense_total
        shared_balance = shared_income_total - shared_expenses_total
        total_income = personal_income + shared_income_total
        total_expense = personal_expense_total + shared_expenses_total
        saving = total_income - total_expense

        goals, _ = await self.goal_repository.list_by_couple(
            couple.id, status=GoalStatus.ACTIVE, limit=5
        )
        goals_data = []
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

        recent_activity = []
        for exp in personal_expenses[:5]:
            recent_activity.append(
                DashboardRecentActivity(
                    id=exp.id,
                    type="expense",
                    description=exp.description,
                    amount=exp.amount,
                    date=exp.expense_date,
                    category=None,
                )
            )

        upcoming_payments = []
        from datetime import date

        today = date.today()
        for exp in personal_expenses:
            if exp.expense_date > today:
                upcoming_payments.append(
                    DashboardUpcomingPayment(
                        id=exp.id,
                        type="expense",
                        description=exp.description,
                        amount=exp.amount,
                        due_date=exp.expense_date,
                        status="pending",
                    )
                )
            if len(upcoming_payments) >= 5:
                break

        statistics = {
            "personal_income": float(personal_income),
            "personal_expense": float(personal_expense_total),
            "shared_income": float(shared_income_total),
            "shared_expense": float(shared_expenses_total),
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(saving),
        }

        ai_recommendations = []
        if total_income > 0:
            savings_rate = float(saving / total_income * 100)
            if savings_rate < 20:
                ai_recommendations.append(
                    "Su tasa de ahorro conjunta es menor al 20%. Revisen gastos compartidos."
                )

        if not ai_recommendations:
            ai_recommendations.append(
                "Registren más transacciones para obtener recomendaciones personalizadas."
            )

        return CoupleDashboardResponse(
            personal_balance=personal_balance,
            shared_balance=shared_balance,
            total_income=total_income,
            total_expense=total_expense,
            shared_income=shared_income_total,
            shared_expense=shared_expenses_total,
            saving=saving,
            goals=goals_data,
            statistics=statistics,
            recent_activity=recent_activity,
            upcoming_payments=upcoming_payments,
            ai_recommendations=ai_recommendations,
        )
