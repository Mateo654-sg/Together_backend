"""
Use Case: CreateGoal (FR-061, FR-064, FR-065, FR-066).

Crea una nueva meta compartida para la pareja o personal.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.couple import CoupleStatus
from app.models.goal import Goal
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import CreateGoalRequest


class CreateGoalUseCase:
    """Use Case: CreateGoal (FR-061, FR-064, FR-065, FR-066).

    Crea una nueva meta compartida para la pareja.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.goal_repository = GoalRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID, data: CreateGoalRequest) -> Goal:
        """Crea una meta.

        Args:
            user_id: UUID del usuario que crea la meta.
            data: Datos de la meta (title, description, target_amount, target_date).

        Returns:
            La meta creada.

        Raises:
            ValidationException: Si la fecha objetivo es en el pasado.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        is_personal = couple is None or couple.status != CoupleStatus.ACCEPTED

        if data.target_date is not None:
            from datetime import date

            if data.target_date < date.today():
                raise ValidationException(
                    "La fecha objetivo no puede ser en el pasado."
                )

        if is_personal:
            goal = Goal(
                couple_id=None,
                user_id=user_id,
                title=data.title.strip(),
                description=data.description,
                image=data.image,
                target_amount=data.target_amount,
                target_date=data.target_date,
            )
        else:
            goal = Goal(
                couple_id=couple.id,
                user_id=None,
                title=data.title.strip(),
                description=data.description,
                image=data.image,
                target_amount=data.target_amount,
                target_date=data.target_date,
            )
        await self.goal_repository.create(goal)
        await self.session.commit()
        return goal
