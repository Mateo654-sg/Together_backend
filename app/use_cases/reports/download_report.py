"""
Use Case: DownloadReport (FR-095, FR-096, FR-097).

Obtiene la información de un reporte para descarga.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportResponse


class DownloadReportUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.report_repository = ReportRepository(session)

    async def execute(
        self, user_id: uuid.UUID, report_id: uuid.UUID
    ) -> ReportResponse:
        report = await self.report_repository.get_by_user_and_id(user_id, report_id)
        if report is None:
            raise NotFoundException("Reporte no encontrado.")

        return ReportResponse.model_validate(report)
