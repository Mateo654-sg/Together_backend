"""
Use Case: ListExports (Tabla 38).

Lista el historial de exportaciones del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.export_repository import ExportRepository
from app.schemas.export import ExportListResponse


class ListExportsUseCase:
    """Use Case: ListExports."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ExportRepository(session)

    async def execute(
        self, user_id: uuid.UUID, *, page: int = 1, limit: int = 20
    ) -> ExportListResponse:
        """Lista el historial de exportaciones con paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.

        Returns:
            ExportListResponse con las exportaciones y datos de paginación.
        """
        items, total = await self.repository.list_by_user(user_id, page=page, limit=limit)

        pages = max(1, -(-total // limit))

        return ExportListResponse(
            data=items,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": pages,
            },
        )
