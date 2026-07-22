"""
Repository de AIHistory.

Encapsula las consultas del historial de IA.
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_history import AIHistory
from app.repositories.base_repository import BaseRepository


class AIHistoryRepository(BaseRepository[AIHistory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIHistory)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[AIHistory], int]:
        base_filter = [
            AIHistory.user_id == user_id,
            AIHistory.deleted_at.is_(None),
        ]

        count_stmt = (
            select(func.count())
            .select_from(AIHistory)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(AIHistory)
            .where(*base_filter)
            .order_by(AIHistory.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, history_id: uuid.UUID
    ) -> AIHistory | None:
        stmt = select(AIHistory).where(
            AIHistory.id == history_id,
            AIHistory.user_id == user_id,
            AIHistory.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
