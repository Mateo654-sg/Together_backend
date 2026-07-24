"""
Repository de SharedIncome (Tabla 9 — Documento 07).

Encapsula las consultas de ingresos compartidos.
"""

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shared_income import SharedIncome
from app.repositories.base_repository import BaseRepository


class SharedIncomeRepository(BaseRepository[SharedIncome]):
    """Repository para el modelo SharedIncome.

    Encapsula las consultas de ingresos compartidos de la pareja.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, SharedIncome)

    async def list_by_couple(
        self,
        couple_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[SharedIncome], int]:
        """Lista ingresos compartidos de la pareja con paginación.

        Args:
            couple_id: UUID de la pareja.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.

        Returns:
            Tupla con la lista de ingresos y el total de registros.
        """
        base_filter = [
            SharedIncome.couple_id == couple_id,
            SharedIncome.deleted_at.is_(None),
        ]

        count_stmt = select(func.count()).select_from(SharedIncome).where(*base_filter)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(SharedIncome)
            .where(*base_filter)
            .order_by(SharedIncome.income_date.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_couple_and_id(
        self, couple_id: uuid.UUID, income_id: uuid.UUID
    ) -> SharedIncome | None:
        """Obtiene un ingreso compartido verificando que pertenezca a la pareja.

        Args:
            couple_id: UUID de la pareja.
            income_id: UUID del ingreso a buscar.

        Returns:
            El ingreso encontrado o None si no existe o no pertenece a la pareja.
        """
        stmt = select(SharedIncome).where(
            SharedIncome.id == income_id,
            SharedIncome.couple_id == couple_id,
            SharedIncome.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_total_by_couple(self, couple_id: uuid.UUID) -> Decimal:
        """Calcula el total de ingresos compartidos de la pareja.

        Args:
            couple_id: UUID de la pareja.

        Returns:
            Suma total de todos los ingresos compartidos como Decimal.
        """
        stmt = select(func.coalesce(func.sum(SharedIncome.amount), 0)).where(
            SharedIncome.couple_id == couple_id,
            SharedIncome.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))
