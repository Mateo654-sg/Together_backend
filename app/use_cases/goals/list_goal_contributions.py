import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.goal_contribution_repository import GoalContributionRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import ContributionListResponse, ContributionResponse


class ListGoalContributionsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = GoalContributionRepository(session)
        self.goal_repository = GoalRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        goal_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> ContributionListResponse:
        couple = await self.couple_repository.get_active_for_user(user_id)
        is_personal = couple is None or couple.status != CoupleStatus.ACCEPTED

        if is_personal:
            goal = await self.goal_repository.get_by_user_and_id(user_id, goal_id)
        else:
            goal = await self.goal_repository.get_by_couple_and_id(couple.id, goal_id)

        if goal is None:
            raise NotFoundException("Meta no encontrada.")

        contributions, total = await self.repository.list_by_goal(
            goal_id, page=page, limit=limit
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
