"""
Use Case: UpdateGoal (FR-062, FR-064, FR-065, FR-066).

Edita una meta existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import UpdateGoalRequest


class UpdateGoalUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.goal_repository = GoalRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self, user_id: uuid.UUID, goal_id: uuid.UUID, data: UpdateGoalRequest
    ):
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        goal = await self.goal_repository.get_by_couple_and_id(couple.id, goal_id)
        if goal is None:
            raise NotFoundException("Meta no encontrada.")

        if data.title is not None:
            goal.title = data.title.strip()
        if data.description is not None:
            goal.description = data.description
        if data.image is not None:
            goal.image = data.image
        if data.target_amount is not None:
            goal.target_amount = data.target_amount
        if data.target_date is not None:
            from datetime import date

            if data.target_date < date.today():
                raise ValidationException("La fecha objetivo no puede ser en el pasado.")
            goal.target_date = data.target_date
        if data.status is not None:
            try:
                goal.status = GoalStatus(data.status)
            except ValueError:
                raise ValidationException(
                    f"Estado inválido. Valores permitidos: {[s.value for s in GoalStatus]}"
                )

        await self.session.commit()
        await self.goal_repository.refresh(goal)
        return goal
