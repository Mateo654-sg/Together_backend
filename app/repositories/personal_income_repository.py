"""
Repository de PersonalIncome (Tabla 6 — Documento 07).

Encapsula las consultas de ingresos personales.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_income import PersonalIncome
from app.repositories.base_repository import BaseRepository


class PersonalIncomeRepository(BaseRepository[PersonalIncome]):
    """Repository para el modelo PersonalIncome.

    Encapsula las consultas de ingresos personales con soporte para
    filtros y paginación.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, PersonalIncome)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[PersonalIncome], int]:
        """Lista ingresos personales con filtros y paginación.

        Args:
            user_id: UUID del usuario propietario de los ingresos.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.
            category_id: Filtrar por categoría específica.
            date_from: Fecha de inicio del rango (inclusive).
            date_to: Fecha de fin del rango (inclusive).

        Returns:
            Tupla con la lista de ingresos y el total de registros.
        """
        base_filter = [
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        ]

        if category_id is not None:
            base_filter.append(PersonalIncome.category_id == category_id)
        if date_from is not None:
            base_filter.append(PersonalIncome.income_date >= date_from)
        if date_to is not None:
            base_filter.append(PersonalIncome.income_date <= date_to)

        count_stmt = (
            select(func.count()).select_from(PersonalIncome).where(*base_filter)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(PersonalIncome)
            .where(*base_filter)
            .order_by(PersonalIncome.income_date.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, income_id: uuid.UUID
    ) -> PersonalIncome | None:
        """Obtiene un ingreso específico verificando que pertenezca al usuario.

        Args:
            user_id: UUID del usuario propietario.
            income_id: UUID del ingreso a buscar.

        Returns:
            El ingreso encontrado o None si no existe o no pertenece al usuario.
        """
        stmt = select(PersonalIncome).where(
            PersonalIncome.id == income_id,
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_total_by_user(self, user_id: uuid.UUID) -> Decimal:
        """Calcula el total de ingresos del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            Suma total de todos los ingresos como Decimal.
        """
        stmt = select(func.coalesce(func.sum(PersonalIncome.amount), 0)).where(
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))
