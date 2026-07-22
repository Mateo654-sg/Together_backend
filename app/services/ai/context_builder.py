"""
Constructor de contexto para la IA.

Recopila información relevante del usuario para enviar al modelo.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository


class AIContextBuilder:
    """Construye contexto financiero para las consultas de IA."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)
        self.couple_repo = CoupleRepository(session)
        self.goal_repo = GoalRepository(session)

    async def build_context(self, user_id: uuid.UUID) -> str:
        """Construye el contexto completo del usuario."""
        parts = []

        total_income = await self.income_repo.get_total_by_user(user_id)
        parts.append(f"Ingresos totales: ${total_income:,.0f} COP")

        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)
        parts.append(f"Gastos totales: ${total_expense:,.0f} COP")

        balance = total_income - total_expense
        parts.append(f"Saldo: ${balance:,.0f} COP")

        if total_income > 0:
            savings_rate = float(balance / total_income * 100)
            parts.append(f"Tasa de ahorro: {savings_rate:.1f}%")

        couple = await self.couple_repo.get_active_for_user(user_id)
        if couple and couple.status == CoupleStatus.ACCEPTED:
            goals, _ = await self.goal_repo.list_by_couple(couple.id, limit=5)
            if goals:
                parts.append(f"Metas activas: {len(goals)}")
                for goal in goals[:3]:
                    progress = float(goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
                    parts.append(f"- {goal.title}: {progress:.0f}% completado")

        if expenses:
            parts.append(f"Últimos {min(len(expenses), 5)} gastos:")
            for exp in expenses[:5]:
                parts.append(f"- ${exp.amount:,.0f} en {exp.description}")

        return "\n".join(parts)
