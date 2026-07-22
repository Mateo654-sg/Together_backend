"""
Use Case: CreateSharedExpense (FR-041, FR-045, FR-047, FR-050).

Registra un gasto compartido y genera la deuda automáticamente
según el tipo de división (50/50, porcentaje, monto personalizado).
"""
import json
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ValidationException
from app.models.debt import Debt
from app.models.shared_expense import SharedExpense, SplitType
from app.repositories.couple_repository import CoupleRepository
from app.repositories.debt_repository import DebtRepository
from app.repositories.shared_category_repository import SharedCategoryRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository
from app.schemas.shared_finance import CreateSharedExpenseRequest


class CreateSharedExpenseUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repository = SharedExpenseRepository(session)
        self.category_repository = SharedCategoryRepository(session)
        self.debt_repository = DebtRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateSharedExpenseRequest
    ) -> SharedExpense:
        from app.models.couple import CoupleStatus

        # Validate user has an active couple
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        # Validate category if provided
        if data.category_id is not None:
            category = await self.category_repository.get_by_couple_and_id(
                couple.id, data.category_id
            )
            if category is None:
                raise ValidationException("La categoría especificada no existe.")

        # Create the shared expense
        expense = SharedExpense(
            couple_id=couple.id,
            category_id=data.category_id,
            paid_by=user_id,
            amount=data.amount,
            description=data.description.strip(),
            notes=data.notes,
            split_type=data.split_type,
            split_details=data.split_details,
            expense_date=data.expense_date,
        )
        await self.expense_repository.create(expense)

        # Determine the partner (the one who didn't pay)
        partner_id = (
            couple.partner_two_id
            if couple.partner_one_id == user_id
            else couple.partner_one_id
        )

        # Generate debt based on split type
        debt_amount = self._calculate_debt_amount(
            data.amount, data.split_type, data.split_details
        )

        if debt_amount > 0:
            debt = Debt(
                debtor_id=partner_id,
                creditor_id=user_id,
                shared_expense_id=expense.id,
                amount=debt_amount,
            )
            await self.debt_repository.create(debt)

        await self.session.commit()
        await self.expense_repository.refresh(expense)
        return expense

    def _calculate_debt_amount(
        self,
        total: Decimal,
        split_type: SplitType,
        split_details: str | None,
    ) -> Decimal:
        if split_type == SplitType.EQUAL:
            return total / 2
        elif split_type == SplitType.PERCENTAGE and split_details:
            details = json.loads(split_details)
            partner_percentage = details.get("partner_percentage", 50)
            return total * Decimal(str(partner_percentage)) / 100
        elif split_type == SplitType.CUSTOM and split_details:
            details = json.loads(split_details)
            return Decimal(str(details.get("partner_amount", 0)))
        return total / 2
