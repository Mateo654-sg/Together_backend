"""
Use Case: DeleteReport.

Elimina (soft delete) un reporte existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.report_repository import ReportRepository


class DeleteReportUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.report_repository = ReportRepository(session)

    async def execute(self, user_id: uuid.UUID, report_id: uuid.UUID) -> None:
        report = await self.report_repository.get_by_user_and_id(user_id, report_id)
        if report is None:
            raise NotFoundException("Reporte no encontrado.")

        await self.report_repository.soft_delete(report)
        await self.session.commit()
