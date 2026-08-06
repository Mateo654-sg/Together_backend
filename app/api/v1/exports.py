"""
Router: /api/v1/exports

Exportaciones de datos financieros (FR-095, FR-096, FR-097, FR-130).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.export import ExportListResponse, ExportRequest
from app.use_cases.exports import ExportFinancesUseCase, ListExportsUseCase

router = APIRouter(prefix="/exports", tags=["Exports"])


def _file_response(result):
    return Response(
        content=result.content,
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


@router.get("", response_model=ExportListResponse)
async def list_exports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """FR-130: Lista el historial de exportaciones."""
    use_case = ListExportsUseCase(db)
    return await use_case.execute(current_user.id, page=page, limit=limit)


@router.post("/pdf", status_code=status.HTTP_200_OK)
async def export_pdf(
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-095: Exporta los movimientos financieros en PDF."""
    use_case = ExportFinancesUseCase(db)
    result = await use_case.execute(
        current_user.id, "pdf", date_from=data.date_from, date_to=data.date_to
    )
    return _file_response(result)


@router.post("/excel", status_code=status.HTTP_200_OK)
async def export_excel(
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-096: Exporta los movimientos financieros en Excel."""
    use_case = ExportFinancesUseCase(db)
    result = await use_case.execute(
        current_user.id, "excel", date_from=data.date_from, date_to=data.date_to
    )
    return _file_response(result)


@router.post("/csv", status_code=status.HTTP_200_OK)
async def export_csv(
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-097: Exporta los movimientos financieros en CSV."""
    use_case = ExportFinancesUseCase(db)
    result = await use_case.execute(
        current_user.id, "csv", date_from=data.date_from, date_to=data.date_to
    )
    return _file_response(result)
