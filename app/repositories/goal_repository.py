"""
Repository de Goal (Tabla 12 — Documento 07).

Encapsula las consultas de metas compartidas.
"""

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal, GoalStatus
from app.repositories.base_repository import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    """Repository para el modelo Goal.

    Encapsula las consultas de metas compartidas de la pareja,
    incluyendo estadísticas y filtrado por estado.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Goal)

    async def list_by_couple(
        self,
        couple_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        status: GoalStatus | None = None,
    ) -> tuple[list[Goal], int]:
        """Lista metas de la pareja con filtros y paginación.

        Args:
            couple_id: UUID de la pareja.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.
            status: Filtrar por estado de la meta (active, completed, cancelled).

        Returns:
            Tupla con la lista de metas y el total de registros.
        """
        base_filter = [
            Goal.couple_id == couple_id,
            Goal.deleted_at.is_(None),
        ]

        if status is not None:
            base_filter.append(Goal.status == status)

        count_stmt = select(func.count()).select_from(Goal).where(*base_filter)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Goal)
            .where(*base_filter)
            .order_by(Goal.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        status: GoalStatus | None = None,
    ) -> tuple[list[Goal], int]:
        """Lista metas personales del usuario con filtros y paginación."""
        base_filter = [
            Goal.user_id == user_id,
            Goal.deleted_at.is_(None),
        ]

        if status is not None:
            base_filter.append(Goal.status == status)

        count_stmt = select(func.count()).select_from(Goal).where(*base_filter)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Goal)
            .where(*base_filter)
            .order_by(Goal.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_couple_and_id(
        self, couple_id: uuid.UUID, goal_id: uuid.UUID
    ) -> Goal | None:
        """Obtiene una meta específica verificando que pertenezca a la pareja.

        Args:
            couple_id: UUID de la pareja.
            goal_id: UUID de la meta a buscar.

        Returns:
            La meta encontrada o None si no existe o no pertenece a la pareja.
        """
        stmt = select(Goal).where(
            Goal.id == goal_id,
            Goal.couple_id == couple_id,
            Goal.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, goal_id: uuid.UUID
    ) -> Goal | None:
        """Obtiene una meta personal específica verificando que pertenezca al usuario."""
        stmt = select(Goal).where(
            Goal.id == goal_id,
            Goal.user_id == user_id,
            Goal.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_statistics(self, couple_id: uuid.UUID) -> dict:
        """Calcula estadísticas generales de metas de la pareja.

        Incluye: total de metas, activas, completadas, monto total ahorrado
        y monto total objetivo.

        Args:
            couple_id: UUID de la pareja.

        Returns:
            Diccionario con las estadísticas de metas.
        """
        active_stmt = (
            select(func.count())
            .select_from(Goal)
            .where(
                Goal.couple_id == couple_id,
                Goal.status == GoalStatus.ACTIVE,
                Goal.deleted_at.is_(None),
            )
        )
        active_count = (await self.session.execute(active_stmt)).scalar_one()

        completed_stmt = (
            select(func.count())
            .select_from(Goal)
            .where(
                Goal.couple_id == couple_id,
                Goal.status == GoalStatus.COMPLETED,
                Goal.deleted_at.is_(None),
            )
        )
        completed_count = (await self.session.execute(completed_stmt)).scalar_one()

        total_saved_stmt = select(
            func.coalesce(func.sum(Goal.current_amount), 0)
        ).where(
            Goal.couple_id == couple_id,
            Goal.deleted_at.is_(None),
        )
        total_saved = Decimal(
            str((await self.session.execute(total_saved_stmt)).scalar_one())
        )

        total_target_stmt = select(
            func.coalesce(func.sum(Goal.target_amount), 0)
        ).where(
            Goal.couple_id == couple_id,
            Goal.deleted_at.is_(None),
        )
        total_target = Decimal(
            str((await self.session.execute(total_target_stmt)).scalar_one())
        )

        return {
            "total_goals": active_count + completed_count,
            "active_goals": active_count,
            "completed_goals": completed_count,
            "total_saved": total_saved,
            "total_target": total_target,
        }

    async def get_statistics_for_user(self, user_id: uuid.UUID) -> dict:
        """Calcula estadísticas generales de metas personales del usuario."""
        active_stmt = (
            select(func.count())
            .select_from(Goal)
            .where(
                Goal.user_id == user_id,
                Goal.status == GoalStatus.ACTIVE,
                Goal.deleted_at.is_(None),
            )
        )
        active_count = (await self.session.execute(active_stmt)).scalar_one()

        completed_stmt = (
            select(func.count())
            .select_from(Goal)
            .where(
                Goal.user_id == user_id,
                Goal.status == GoalStatus.COMPLETED,
                Goal.deleted_at.is_(None),
            )
        )
        completed_count = (await self.session.execute(completed_stmt)).scalar_one()

        total_saved_stmt = select(
            func.coalesce(func.sum(Goal.current_amount), 0)
        ).where(
            Goal.user_id == user_id,
            Goal.deleted_at.is_(None),
        )
        total_saved = Decimal(
            str((await self.session.execute(total_saved_stmt)).scalar_one())
        )

        total_target_stmt = select(
            func.coalesce(func.sum(Goal.target_amount), 0)
        ).where(
            Goal.user_id == user_id,
            Goal.deleted_at.is_(None),
        )
        total_target = Decimal(
            str((await self.session.execute(total_target_stmt)).scalar_one())
        )

        return {
            "total_goals": active_count + completed_count,
            "active_goals": active_count,
            "completed_goals": completed_count,
            "total_saved": total_saved,
            "total_target": total_target,
        }
