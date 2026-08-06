"""
Use Case: ExportFinances (FR-095 a FR-097, FR-130).

Genera un archivo (PDF/Excel/CSV) con los movimientos del usuario
y registra la exportación en el historial (Tabla 38).
"""

import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.export_record import Export, ExportFormat
from app.repositories.export_repository import ExportRepository
from app.use_cases.exports.build_export_data import ExportDataBuilder
from app.use_cases.exports.generate_csv import generate_csv
from app.use_cases.exports.generate_excel import generate_excel
from app.use_cases.exports.generate_pdf import generate_pdf


@dataclass
class ExportResult:
    filename: str
    media_type: str
    content: bytes
    export: Export


MEDIA_TYPES = {
    ExportFormat.PDF: "application/pdf",
    ExportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ExportFormat.CSV: "text/csv; charset=utf-8",
}


class ExportFinancesUseCase:
    """Use Case: ExportFinances (FR-095 a FR-097)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.export_repository = ExportRepository(session)
        self.data_builder = ExportDataBuilder(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        export_format: str,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> ExportResult:
        """Genera y registra una exportación de los movimientos del usuario.

        Args:
            user_id: UUID del usuario propietario.
            export_format: Formato solicitado (pdf, excel, csv).
            date_from: Fecha de inicio del rango (inclusive).
            date_to: Fecha de fin del rango (inclusive).

        Returns:
            ExportResult con el nombre de archivo, media type, contenido y registro.

        Raises:
            ValidationException: Si el formato no es válido o el rango es inválido.
        """
        try:
            format_enum = ExportFormat(export_format)
        except ValueError:
            raise ValidationException(
                f"Formato inválido. Permitidos: {[f.value for f in ExportFormat]}"
            )

        if date_from is not None and date_to is not None and date_from > date_to:
            raise ValidationException("La fecha inicial debe ser anterior o igual a la final.")

        rows = await self.data_builder.build(
            user_id, date_from=date_from, date_to=date_to
        )

        if format_enum == ExportFormat.PDF:
            content = generate_pdf(rows)
        elif format_enum == ExportFormat.EXCEL:
            content = generate_excel(rows)
        else:
            content = generate_csv(rows)

        extension = format_enum.value if format_enum != ExportFormat.EXCEL else "xlsx"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"together_export_{stamp}.{extension}"

        record = Export(
            user_id=user_id,
            format=format_enum,
            date_from=date_from,
            date_to=date_to,
            file_size=len(content),
            generated_at=datetime.now(timezone.utc),
        )
        await self.export_repository.create(record)
        await self.session.commit()

        return ExportResult(
            filename=filename,
            media_type=MEDIA_TYPES[format_enum],
            content=content,
            export=record,
        )
