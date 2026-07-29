"""
Use Case: ContributeToGoal (FR-067, FR-068, FR-069).

Registra un aporte o retiro a una meta y actualiza el progreso automáticamente.
"""

import uuid
from datetime import date, datetime, time, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundException,
    ValidationException,
)
from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.models.goal_contribution import GoalContribution
from app.models.personal_expense import PersonalExpense
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_contribution_repository import GoalContributionRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.schemas.goal import CreateContributionRequest


class ContributeToGoalUseCase:
    """Use Case: ContributeToGoal (FR-067, FR-068, FR-069).

    Registra un aporte o retiro a una meta y actualiza el progreso automáticamente.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.goal_repository = GoalRepository(session)
        self.contribution_repository = GoalContributionRepository(session)
        self.couple_repository = CoupleRepository(session)
        self.expense_repository = PersonalExpenseRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateContributionRequest
    ) -> GoalContribution:
        """Registra un aporte a una meta y actualiza su progreso.

        Args:
            user_id: UUID del usuario que aporta.
            data: Datos del aporte (goal_id, amount).

        Returns:
            El aporte registrado.

        Raises:
            NotFoundException: Si la meta no existe.
            ValidationException: Si la meta no está activa.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        is_personal = couple is None or couple.status != CoupleStatus.ACCEPTED

        if is_personal:
            goal = await self.goal_repository.get_by_user_and_id(user_id, data.goal_id)
        else:
            goal = await self.goal_repository.get_by_couple_and_id(couple.id, data.goal_id)

        if goal is None:
            raise NotFoundException("Meta no encontrada.")

        if goal.status != GoalStatus.ACTIVE:
            raise ValidationException(
                "Solo se pueden realizar aportes a metas activas."
            )

        balance = await self.expense_repository.get_balance(user_id)
        if data.amount > balance:
            raise ValidationException(
                "No puedes aportar más dinero del saldo disponible."
            )

        contribution_day = data.contribution_date or date.today()
        contribution_datetime = datetime.combine(
            contribution_day, time.min, tzinfo=timezone.utc
        )

        contribution = GoalContribution(
            goal_id=goal.id,
            user_id=user_id,
            amount=data.amount,
            contribution_date=contribution_datetime,
        )
        await self.contribution_repository.create(contribution)

        expense = PersonalExpense(
            user_id=user_id,
            category_id=None,
            amount=data.amount,
            description="Aporte a meta",
            notes=goal.title,
            payment_method="Ahorro",
            location=None,
            attachment_url=None,
            expense_date=contribution_day,
        )
        await self.expense_repository.create(expense)

        goal.current_amount = goal.current_amount + data.amount

        if goal.current_amount >= goal.target_amount:
            goal.status = GoalStatus.COMPLETED

        await self.session.commit()
        return contribution
