"""
Router: /api/v1/reports

Reportes financieros (FR-089 a FR-097).
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.report import (
    GenerateReportRequest,
    ReportListResponse,
    ReportResponse,
)
from app.use_cases.reports.delete_report import DeleteReportUseCase
from app.use_cases.reports.download_report import DownloadReportUseCase
from app.use_cases.reports.generate_report import GenerateReportUseCase
from app.use_cases.reports.list_reports import ListReportsUseCase

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=ReportListResponse)
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """FR-089: Lista reportes generados."""
    use_case = ListReportsUseCase(db)
    return await use_case.execute(current_user.id, page=page, limit=limit)


@router.post(
    "", response_model=ReportResponse, status_code=status.HTTP_201_CREATED
)
async def generate_report(
    data: GenerateReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-089 a FR-097: Genera un nuevo reporte."""
    use_case = GenerateReportUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.get("/{report_id}", response_model=ReportResponse)
async def download_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-095 a FR-097: Obtiene información de un reporte para descarga."""
    use_case = DownloadReportUseCase(db)
    return await use_case.execute(current_user.id, report_id)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Eliminar un reporte (soft delete)."""
    use_case = DeleteReportUseCase(db)
    await use_case.execute(current_user.id, report_id)
