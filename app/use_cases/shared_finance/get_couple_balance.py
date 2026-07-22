"""
Use Case: GetCoupleBalance (FR-051).

Retorna el balance financiero entre la pareja: cuánto ha pagado
cada uno y la diferencia.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository
from app.repositories.shared_income_repository import SharedIncomeRepository
from app.schemas.shared_finance import CoupleBalanceResponse


class GetCoupleBalanceUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.couple_repository = CoupleRepository(session)
        self.expense_repository = SharedExpenseRepository(session)
        self.income_repository = SharedIncomeRepository(session)

    async def execute(self, user_id: uuid.UUID) -> CoupleBalanceResponse:
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        total_expenses = await self.expense_repository.get_total_by_couple(couple.id)
        total_incomes = await self.income_repository.get_total_by_couple(couple.id)

        partner_one_paid = await self.expense_repository.get_paid_by_partner(
            couple.id, couple.partner_one_id
        )
        partner_two_paid = await self.expense_repository.get_paid_by_partner(
            couple.id, couple.partner_two_id
        )

        # Balance: positive means partner_one is owed money
        half = total_expenses / 2
        balance = partner_one_paid - half

        return CoupleBalanceResponse(
            total_shared_expenses=total_expenses,
            total_shared_incomes=total_incomes,
            balance=balance,
            partner_one_paid=partner_one_paid,
            partner_two_paid=partner_two_paid,
        )
