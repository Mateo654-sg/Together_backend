"""
Repository de GoalContribution (Tabla 13 — Documento 07).

Encapsula las consultas de aportes a metas.
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal_contribution import GoalContribution
from app.repositories.base_repository import BaseRepository


class GoalContributionRepository(BaseRepository[GoalContribution]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, GoalContribution)

    async def list_by_goal(
        self,
        goal_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[GoalContribution], int]:
        base_filter = [GoalContribution.goal_id == goal_id]

        count_stmt = (
            select(func.count())
            .select_from(GoalContribution)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(GoalContribution)
            .where(*base_filter)
            .order_by(GoalContribution.contribution_date.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def list_by_couple(
        self,
        couple_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[GoalContribution], int]:
        from app.models.goal import Goal

        base_filter = [
            Goal.couple_id == couple_id,
        ]

        count_stmt = (
            select(func.count())
            .select_from(GoalContribution)
            .join(Goal, GoalContribution.goal_id == Goal.id)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(GoalContribution)
            .join(Goal, GoalContribution.goal_id == Goal.id)
            .where(*base_filter)
            .order_by(GoalContribution.contribution_date.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_total_by_goal(self, goal_id: uuid.UUID) -> float:
        stmt = select(
            func.coalesce(func.sum(GoalContribution.amount), 0)
        ).where(GoalContribution.goal_id == goal_id)
        result = await self.session.execute(stmt)
        return float(result.scalar_one())
