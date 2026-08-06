"""
Use Case: GetCoupleStatistics (FR-093).

Obtiene estadísticas financieras de la pareja.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.financial_engine import savings_rate as fre_savings_rate
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository
from app.repositories.shared_income_repository import SharedIncomeRepository
from app.schemas.report import CoupleStatisticsResponse


class GetCoupleStatisticsUseCase:
    """Use Case: GetCoupleStatistics (FR-093).

    Combina finanzas personales y compartidas de la pareja,
    incluyendo la contribución de cada integrante.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)
        self.personal_income_repo = PersonalIncomeRepository(session)
        self.personal_expense_repo = PersonalExpenseRepository(session)
        self.shared_income_repo = SharedIncomeRepository(session)
        self.shared_expense_repo = SharedExpenseRepository(session)

    async def execute(self, user_id: uuid.UUID) -> CoupleStatisticsResponse:
        """Calcula estadísticas de la pareja del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            CoupleStatisticsResponse con totales personales/compartidos
            y contribución de cada integrante.

        Raises:
            ConflictException: Si el usuario no tiene pareja vinculada.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        partner_one_id = couple.partner_one_id
        partner_two_id = couple.partner_two_id or partner_one_id

        personal_income = await self.personal_income_repo.get_total_by_user(user_id)
        personal_expenses, _ = await self.personal_expense_repo.list_by_user(
            user_id, page=1, limit=1000
        )
        personal_expense = sum(e.amount for e in personal_expenses)

        shared_income = await self.shared_income_repo.get_total_by_couple(couple.id)
        shared_expense = await self.shared_expense_repo.get_total_by_couple(couple.id)

        total_income = personal_income + shared_income
        total_expense = personal_expense + shared_expense
        balance = total_income - total_expense

        savings_rate = float(fre_savings_rate(total_income, total_expense))

        partner_one_income = await self.personal_income_repo.get_total_by_user(
            partner_one_id
        )
        partner_two_income = await self.personal_income_repo.get_total_by_user(
            partner_two_id
        )
        partner_one_paid = await self.shared_expense_repo.get_paid_by_partner(
            couple.id, partner_one_id
        )
        partner_two_paid = await self.shared_expense_repo.get_paid_by_partner(
            couple.id, partner_two_id
        )

        partner_contribution = {
            str(partner_one_id): {
                "income": float(partner_one_income),
                "shared_expenses_paid": float(partner_one_paid),
            },
            str(partner_two_id): {
                "income": float(partner_two_income),
                "shared_expenses_paid": float(partner_two_paid),
            },
        }

        return CoupleStatisticsResponse(
            personal_income=personal_income,
            personal_expense=personal_expense,
            shared_income=shared_income,
            shared_expense=shared_expense,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            savings_rate=round(savings_rate, 2),
            partner_contribution=partner_contribution,
        )
