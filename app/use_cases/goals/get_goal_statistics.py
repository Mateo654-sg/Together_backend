"""
Use Case: GetGoalStatistics (FR-069, FR-070, FR-071, FR-072).

Obtiene estadísticas generales de las metas de la pareja o personales.
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import GoalStatisticsResponse


class GetGoalStatisticsUseCase:
    """Use Case: GetGoalStatistics (FR-069, FR-070, FR-071, FR-072).

    Obtiene estadísticas generales de las metas de la pareja o personales,
    incluyendo progreso general y metas en/desde fecha.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.goal_repository = GoalRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(self, user_id: uuid.UUID) -> GoalStatisticsResponse:
        """Calcula estadísticas de metas.

        Args:
            user_id: UUID del usuario.

        Returns:
            GoalStatisticsResponse con totales, progreso y estado de cada meta.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        is_personal = couple is None or couple.status != CoupleStatus.ACCEPTED

        if is_personal:
            stats = await self.goal_repository.get_statistics_for_user(user_id)
            goals, _ = await self.goal_repository.list_by_user(
                user_id, status=GoalStatus.ACTIVE
            )
        else:
            stats = await self.goal_repository.get_statistics(couple.id)
            goals, _ = await self.goal_repository.list_by_couple(
                couple.id, status=GoalStatus.ACTIVE
            )

        goals_on_track = 0
        goals_behind = 0
        for goal in goals:
            if goal.target_date is None:
                goals_on_track += 1
                continue

            days_remaining = (goal.target_date - date.today()).days
            if days_remaining <= 0:
                goals_behind += 1
                continue

            progress = (
                float(goal.current_amount / goal.target_amount)
                if goal.target_amount > 0
                else 0
            )
            days_elapsed = (date.today() - goal.created_at.date()).days
            if days_elapsed <= 0:
                goals_on_track += 1
                continue

            expected_progress = days_elapsed / (
                (goal.target_date - goal.created_at.date()).days or 1
            )
            if progress >= expected_progress:
                goals_on_track += 1
            else:
                goals_behind += 1

        overall_progress = (
            float(stats["total_saved"] / stats["total_target"] * 100)
            if stats["total_target"] > 0
            else 0.0
        )

        return GoalStatisticsResponse(
            total_goals=stats["total_goals"],
            active_goals=stats["active_goals"],
            completed_goals=stats["completed_goals"],
            total_saved=stats["total_saved"],
            total_target=stats["total_target"],
            overall_progress_percentage=min(overall_progress, 100.0),
            goals_on_track=goals_on_track,
            goals_behind=goals_behind,
        )
