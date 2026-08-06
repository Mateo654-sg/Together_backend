import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.financial_engine.goals import (
    goal_days_remaining,
    goal_predicted_completion,
    goal_progress,
)
from app.models.couple import CoupleStatus
from app.models.goal import Goal
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import GoalResponse


class GetGoalUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.goal_repository = GoalRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> GoalResponse:
        couple = await self.couple_repository.get_active_for_user(user_id)
        is_personal = couple is None or couple.status != CoupleStatus.ACCEPTED

        if is_personal:
            goal = await self.goal_repository.get_by_user_and_id(user_id, goal_id)
        else:
            goal = await self.goal_repository.get_by_couple_and_id(couple.id, goal_id)

        if goal is None:
            raise NotFoundException("Meta no encontrada.")

        goal_data = GoalResponse.model_validate(goal)
        goal_data.progress_percentage = self._calculate_progress(goal)
        goal_data.days_remaining = self._calculate_days_remaining(goal)
        goal_data.predicted_completion_date = self._predict_completion(goal)
        return goal_data

    @staticmethod
    def _calculate_progress(goal: Goal) -> float | None:
        if goal.target_amount <= 0:
            return None
        return float(goal_progress(goal.current_amount, goal.target_amount))

    @staticmethod
    def _calculate_days_remaining(goal: Goal) -> int | None:
        if goal.target_date is None:
            return None
        return goal_days_remaining(goal.target_date)

    @staticmethod
    def _predict_completion(goal: Goal):
        if goal.target_amount <= 0 or goal.current_amount <= 0:
            return None
        if goal.target_date is None:
            return None
        return goal_predicted_completion(
            goal.current_amount,
            goal.target_amount,
            goal.created_at.date(),
            goal.target_date,
        )
