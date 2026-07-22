"""
Repository de Report.

Encapsula las consultas de reportes generados.
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.repositories.base_repository import BaseRepository


class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Report)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Report], int]:
        base_filter = [
            Report.user_id == user_id,
            Report.deleted_at.is_(None),
        ]

        count_stmt = (
            select(func.count())
            .select_from(Report)
            .where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Report)
            .where(*base_filter)
            .order_by(Report.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, report_id: uuid.UUID
    ) -> Report | None:
        stmt = select(Report).where(
            Report.id == report_id,
            Report.user_id == user_id,
            Report.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_user(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(Report).where(
            Report.user_id == user_id,
            Report.deleted_at.is_(None),
        )
        return (await self.session.execute(stmt)).scalar_one()
