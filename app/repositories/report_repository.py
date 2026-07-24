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
    """Repository para el modelo Report.

    Encapsula las consultas de reportes financieros generados por el usuario.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Report)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Report], int]:
        """Lista reportes del usuario con paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.

        Returns:
            Tupla con la lista de reportes y el total de registros.
        """
        base_filter = [
            Report.user_id == user_id,
            Report.deleted_at.is_(None),
        ]

        count_stmt = select(func.count()).select_from(Report).where(*base_filter)
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
        """Obtiene un reporte verificando que pertenezca al usuario.

        Args:
            user_id: UUID del usuario propietario.
            report_id: UUID del reporte a buscar.

        Returns:
            El reporte encontrado o None si no existe o no pertenece al usuario.
        """
        stmt = select(Report).where(
            Report.id == report_id,
            Report.user_id == user_id,
            Report.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """Cuenta el total de reportes del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            Cantidad total de reportes del usuario.
        """
        stmt = (
            select(func.count())
            .select_from(Report)
            .where(
                Report.user_id == user_id,
                Report.deleted_at.is_(None),
            )
        )
        return (await self.session.execute(stmt)).scalar_one()
