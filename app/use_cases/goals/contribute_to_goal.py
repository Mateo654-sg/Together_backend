"""
Use Case: ContributeToGoal (FR-067, FR-068, FR-069).

Registra un aporte o retiro a una meta y actualiza el progreso automáticamente.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundException,
    ValidationException,
)
from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.models.goal_contribution import GoalContribution
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_contribution_repository import GoalContributionRepository
from app.repositories.goal_repository import GoalRepository
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

        contribution = GoalContribution(
            goal_id=goal.id,
            user_id=user_id,
            amount=data.amount,
        )
        await self.contribution_repository.create(contribution)

        goal.current_amount = goal.current_amount + data.amount

        if goal.current_amount >= goal.target_amount:
            goal.status = GoalStatus.COMPLETED

        await self.session.commit()
        return contribution
