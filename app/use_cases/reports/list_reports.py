"""
Use Case: ListReports.

Lista los reportes generados por el usuario.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportListResponse, ReportResponse


class ListReportsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.report_repository = ReportRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> ReportListResponse:
        reports, total = await self.report_repository.list_by_user(
            user_id, page=page, limit=limit
        )

        data = [ReportResponse.model_validate(r) for r in reports]

        return ReportListResponse(
            data=data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )
