"""
Use Case: ListGoals (FR-061-List).

Lista las metas compartidas de la pareja con paginación y filtro por estado.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.financial_engine.goals import (
    goal_days_remaining,
    goal_predicted_completion,
    goal_progress,
)
from app.models.couple import CoupleStatus
from app.models.goal import GoalStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import GoalListResponse, GoalResponse


class ListGoalsUseCase:
    """Use Case: ListGoals (FR-061-List).

    Lista las metas compartidas de la pareja con paginación y filtro por estado.
    """

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
        """Lista metas con cálculo de progreso y predicciones.

        Args:
            user_id: UUID del usuario.
            page: Número de página.
            limit: Cantidad máxima de resultados.
            status: Filtrar por estado de la meta.

        Returns:
            GoalListResponse con metas enriquecidas (progreso, días restantes, predicción).

        Raises:
            ConflictException: Si el usuario no tiene una pareja activa.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException(
                "Necesitas una pareja activa para consultar metas compartidas."
            )

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

    @staticmethod
    def _calculate_progress(goal) -> float | None:
        if goal.target_amount <= 0:
            return None
        return float(goal_progress(goal.current_amount, goal.target_amount))

    @staticmethod
    def _calculate_days_remaining(goal) -> int | None:
        if goal.target_date is None:
            return None
        return goal_days_remaining(goal.target_date)

    @staticmethod
    def _predict_completion(goal):
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
