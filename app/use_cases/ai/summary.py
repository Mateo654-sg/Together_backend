"""
Use Case: AISummary (FR-101, FR-102).

Genera resúmenes semanales y mensuales.

Los KPIs los calcula el Financial Rules Engine; la IA solo redacta.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.financial_engine import net_cash_flow, savings_rate
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.ai import AISummaryRequest, AISummaryResponse
from app.services.ai.service import AIService


class AISummaryUseCase:
    """Use Case: AISummary (FR-101, FR-102).

    Genera resúmenes semanales y mensuales de las finanzas del usuario
    con KPIs calculados por el Financial Rules Engine.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: AISummaryRequest, summary_type: str = "monthly"
    ) -> AISummaryResponse:
        """Genera un resumen financiero con KPIs reales.

        Args:
            user_id: UUID del usuario.
            data: Datos de la solicitud.
            summary_type: Tipo de resumen ("weekly" o "monthly").

        Returns:
            AISummaryResponse con el período, resumen, highlights y KPIs.
        """
        if summary_type == "weekly":
            question = "Genera un resumen financiero de esta semana."
            period = "Semanal"
        else:
            question = "Genera un resumen financiero de este mes."
            period = "Mensual"

        result = await self.ai_service.chat(
            user_id, question, endpoint=f"{summary_type}-summary"
        )

        total_income = await self.income_repo.get_total_by_user(user_id)
        expenses, _ = await self.expense_repo.list_by_user(user_id, page=1, limit=1000)
        total_expense = sum(e.amount for e in expenses)
        savings = net_cash_flow(total_income, total_expense)
        saving_rate = savings_rate(total_income, total_expense)

        kpis = {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "savings": float(savings),
            "savings_rate": float(saving_rate),
            "transactions": len(expenses) + len(await self.income_repo.list_by_user(user_id, page=1, limit=1000)),
        }

        highlights = self._build_highlights(saving_rate, savings, len(expenses))

        return AISummaryResponse(
            period=period,
            summary=result["answer"],
            highlights=highlights,
            kpis=kpis,
        )

    @staticmethod
    def _build_highlights(saving_rate, savings, transaction_count: int) -> list[str]:
        highlights = []
        if saving_rate >= 30:
            highlights.append(f"Ahorro acumulado del {float(saving_rate):.0f}% de ingresos.")
        else:
            highlights.append("Registra tus movimientos para mejorar tu tasa de ahorro.")
        if savings > 0:
            highlights.append("Ingresos superan a los gastos en el período.")
        else:
            highlights.append("Revisa tus gastos: los gastos superan los ingresos.")
        highlights.append(f"{transaction_count} transacciones registradas en el período.")
        return highlights
