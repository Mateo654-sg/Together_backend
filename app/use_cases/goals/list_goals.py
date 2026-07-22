"""
Use Case: ListGoals (FR-061-List).

Lista las metas de la pareja con paginación y filtro por estado.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import GoalListResponse, GoalResponse


class ListGoalsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.goal_repository = GoalRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        status: GoalStatus | None = None,
    ) -> GoalListResponse:
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        goals, total = await self.goal_repository.list_by_couple(
            couple.id, page=page, limit=limit, status=status
        )

        data = []
        for goal in goals:
            goal_data = GoalResponse.model_validate(goal)
            goal_data.progress_percentage = self._calculate_progress(goal)
            goal_data.days_remaining = self._calculate_days_remaining(goal)
            goal_data.predicted_completion_date = self._predict_completion(goal)
            data.append(goal_data)

        return GoalListResponse(
            data=data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )

    def _calculate_progress(self, goal) -> float | None:
        if goal.target_amount <= 0:
            return None
        return min(float(goal.current_amount / goal.target_amount * 100), 100.0)

    def _calculate_days_remaining(self, goal) -> int | None:
        if goal.target_date is None:
            return None
        from datetime import date

        delta = goal.target_date - date.today()
        return max(delta.days, 0)

    def _predict_completion(self, goal):
        if goal.target_amount <= 0 or goal.current_amount <= 0:
            return None
        if goal.target_date is None:
            return None
        from datetime import date, timedelta

        progress_ratio = float(goal.current_amount / goal.target_amount)
        if progress_ratio >= 1.0:
            return date.today()

        days_elapsed = (date.today() - goal.created_at.date()).days
        if days_elapsed <= 0:
            return goal.target_date

        daily_rate = float(goal.current_amount) / days_elapsed
        remaining_amount = float(goal.target_amount - goal.current_amount)
        if daily_rate <= 0:
            return goal.target_date

        days_needed = int(remaining_amount / daily_rate)
        predicted = date.today() + timedelta(days=days_needed)
        return predicted

    def _calculate_progress(self, goal) -> float | None:
        if goal.target_amount <= 0:
            return None
        return min(float(goal.current_amount / goal.target_amount * 100), 100.0)
