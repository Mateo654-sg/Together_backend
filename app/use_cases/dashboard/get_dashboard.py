"""
Use Case: GetDashboard (FR-079 a FR-088).

Agrega datos de todos los módulos para el dashboard principal.
"""

import uuid
from datetime import date
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.personal_category_repository import PersonalCategoryRepository
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
    """Use Case: GetDashboard (FR-079 a FR-088).

    Agrega datos de todos los módulos para el dashboard principal:
    balance, ingresos, gastos, metas recientes, actividad reciente,
    pagos próximos y recomendaciones de IA.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.personal_expense_repo = PersonalExpenseRepository(session)
        self.personal_income_repo = PersonalIncomeRepository(session)
        self.personal_category_repo = PersonalCategoryRepository(session)
        self.shared_expense_repo = SharedExpenseRepository(session)
        self.shared_income_repo = SharedIncomeRepository(session)
        self.couple_repository = CoupleRepository(session)
        self.goal_repository = GoalRepository(session)

    async def execute(self, user_id: uuid.UUID) -> DashboardResponse:
        """Construye el dashboard principal del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            DashboardResponse con balance, metas, actividad, pagos y recomendaciones.
        """
        total_income = await self.personal_income_repo.get_total_by_user(user_id)
        total_expense = Decimal("0")
        expenses, _ = await self.personal_expense_repo.list_by_user(
            user_id, page=1, limit=1000, sort_by="created_at"
        )
        incomes, _ = await self.personal_income_repo.list_by_user(
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
                couple.id, limit=5
            )
        else:
            goals, _ = await self.goal_repository.list_by_user(user_id, limit=5)

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

        categories = await self.personal_category_repo.list_by_user(user_id)
        category_names = {category.id: category.name for category in categories}
        recent_activity = self._build_recent_activity(
            expenses, incomes, category_names
        )

        upcoming_payments = self._build_upcoming_payments(expenses)

        statistics = {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(balance),
            "savings_rate": float(saving / total_income * 100)
            if total_income > 0
            else 0.0,
            "transaction_count": len(expenses) + len(incomes),
            "monthly_breakdown": self._build_monthly_breakdown(expenses, incomes),
            "top_categories": self._build_top_categories(expenses, category_names),
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

    def _build_recent_activity(
        self, expenses, incomes, category_names: dict[uuid.UUID, str]
    ) -> list[DashboardRecentActivity]:
        activities = []
        for exp in expenses:
            activities.append(
                DashboardRecentActivity(
                    id=exp.id,
                    type="expense",
                    description=exp.description,
                    amount=exp.amount,
                    date=exp.created_at,
                    category=category_names.get(exp.category_id) or exp.payment_method,
                )
            )
        for income in incomes:
            activities.append(
                DashboardRecentActivity(
                    id=income.id,
                    type="income",
                    description=income.description,
                    amount=income.amount,
                    date=income.created_at,
                    category=category_names.get(income.category_id) or "Ingreso",
                )
            )
        return sorted(activities, key=lambda item: item.date, reverse=True)[:10]

    def _build_monthly_breakdown(self, expenses, incomes) -> list[dict]:
        buckets: dict[tuple[int, int], dict[str, Decimal]] = defaultdict(
            lambda: {"income": Decimal("0"), "expense": Decimal("0")}
        )

        for income in incomes:
            key = (income.income_date.year, income.income_date.month)
            buckets[key]["income"] += income.amount

        for expense in expenses:
            key = (expense.expense_date.year, expense.expense_date.month)
            buckets[key]["expense"] += expense.amount

        return [
            {
                "month": date(year, month, 1).strftime("%b %Y"),
                "income": float(values["income"]),
                "expense": float(values["expense"]),
            }
            for (year, month), values in sorted(buckets.items())
        ]

    def _build_top_categories(
        self, expenses, category_names: dict[uuid.UUID, str]
    ) -> list[dict]:
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for expense in expenses:
            category_name = category_names.get(expense.category_id) or "Sin categoría"
            totals[category_name] += expense.amount

        total_expense = sum(totals.values(), Decimal("0"))
        if total_expense <= 0:
            return []

        return [
            {
                "category_name": name,
                "total_amount": float(amount),
                "percentage_of_total": float(amount / total_expense * 100),
            }
            for name, amount in sorted(
                totals.items(), key=lambda item: item[1], reverse=True
            )
            if amount > 0
        ]

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
