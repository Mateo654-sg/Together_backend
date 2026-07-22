"""
Use Case: DeleteGoal (FR-063).

Elimina (soft delete) una meta existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository


class DeleteGoalUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.goal_repository = GoalRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        goal = await self.goal_repository.get_by_couple_and_id(couple.id, goal_id)
        if goal is None:
            raise NotFoundException("Meta no encontrada.")

        await self.goal_repository.soft_delete(goal)
        await self.session.commit()
