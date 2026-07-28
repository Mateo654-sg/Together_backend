"""
Use Case: ListGoalHistory.

Lista el historial de aportes de la pareja o personales.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_contribution_repository import GoalContributionRepository
from app.schemas.goal import ContributionListResponse, ContributionResponse


class ListGoalHistoryUseCase:
    """Use Case: ListGoalHistory.

    Lista el historial de aportes de la pareja o personales.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.contribution_repository = GoalContributionRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> ContributionListResponse:
        """Lista el historial de aportes a metas.

        Args:
            user_id: UUID del usuario.
            page: Número de página.
            limit: Cantidad máxima de resultados.

        Returns:
            ContributionListResponse con los aportes y paginación.
        """
        couple = await self.couple_repository.get_active_for_user(user_id)
        is_personal = couple is None or couple.status != CoupleStatus.ACCEPTED

        if is_personal:
            contributions, total = await self.contribution_repository.list_by_user(
                user_id, page=page, limit=limit
            )
        else:
            contributions, total = await self.contribution_repository.list_by_couple(
                couple.id, page=page, limit=limit
            )

        data = [ContributionResponse.model_validate(c) for c in contributions]

        return ContributionListResponse(
            data=data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )
