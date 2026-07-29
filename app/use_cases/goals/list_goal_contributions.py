import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.goal_contribution_repository import GoalContributionRepository
from app.schemas.goal import ContributionListResponse, ContributionResponse


class ListGoalContributionsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = GoalContributionRepository(session)

    async def execute(
        self,
        goal_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> ContributionListResponse:
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
