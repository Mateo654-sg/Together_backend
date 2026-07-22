"""
Use Case: GenerateReport (FR-089 a FR-097).

Genera un reporte financiero en el formato solicitado.
"""
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, ReportFormat, ReportStatus, ReportType
from app.repositories.report_repository import ReportRepository
from app.schemas.report import GenerateReportRequest


class GenerateReportUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.report_repository = ReportRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: GenerateReportRequest
    ) -> Report:
        try:
            report_type = ReportType(data.report_type)
        except ValueError:
            from app.core.exceptions import ValidationException

            raise ValidationException(
                f"Tipo de reporte inválido. Permitidos: {[t.value for t in ReportType]}"
            )

        try:
            report_format = ReportFormat(data.format)
        except ValueError:
            from app.core.exceptions import ValidationException

            raise ValidationException(
                f"Formato inválido. Permitidos: {[f.value for f in ReportFormat]}"
            )

        parameters = {}
        if data.month is not None:
            parameters["month"] = data.month
        if data.year is not None:
            parameters["year"] = data.year
        if data.category_id is not None:
            parameters["category_id"] = str(data.category_id)

        report = Report(
            user_id=user_id,
            report_type=report_type,
            format=report_format,
            status=ReportStatus.COMPLETED,
            parameters=json.dumps(parameters) if parameters else None,
            generated_at=datetime.now(timezone.utc),
        )
        await self.report_repository.create(report)
        await self.session.commit()
        await self.report_repository.refresh(report)
        return report
