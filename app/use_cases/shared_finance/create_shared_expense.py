"""
Use Case: CreateSharedExpense (FR-041, FR-045, FR-047, FR-050).

Registra un gasto compartido y genera la deuda automáticamente
según el tipo de división (50/50, porcentaje, monto personalizado).
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ValidationException
from app.models.debt import Debt
from app.models.shared_expense import SharedExpense
from app.repositories.couple_repository import CoupleRepository
from app.repositories.debt_repository import DebtRepository
from app.repositories.shared_category_repository import SharedCategoryRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository
from app.schemas.shared_finance import CreateSharedExpenseRequest
from app.use_cases.shared_finance.split_utils import calculate_debt_amount


class CreateSharedExpenseUseCase:
    """Use Case: CreateSharedExpense (FR-041, FR-045, FR-047, FR-050).

    Registra un gasto compartido y genera la deuda automáticamente
    según el tipo de división (50/50, porcentaje, monto personalizado).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repository = SharedExpenseRepository(session)
        self.category_repository = SharedCategoryRepository(session)
        self.debt_repository = DebtRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateSharedExpenseRequest
    ) -> SharedExpense:
        """Crea un gasto compartido y genera la deuda correspondiente.

        Args:
            user_id: UUID del usuario que paga el gasto.
            data: Datos del gasto compartido.

        Returns:
            El gasto compartido creado.

        Raises:
            ConflictException: Si el usuario no tiene pareja vinculada.
            ValidationException: Si la categoría especificada no existe.
        """
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
        debt_amount = calculate_debt_amount(
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
        return expense
