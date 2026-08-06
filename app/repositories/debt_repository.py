"""
Repository de Debt (Tabla 10 — Documento 07).

Encapsula las consultas de deudas entre pareja.
"""

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.debt import Debt, DebtStatus
from app.repositories.base_repository import BaseRepository


class DebtRepository(BaseRepository[Debt]):
    """Repository para el modelo Debt.

    Encapsula las consultas de deudas entre pareja.
    Las deudas se generan automáticamente al crear gastos compartidos.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Debt)

    async def list_pending_for_user(self, user_id: uuid.UUID) -> list[Debt]:
        """Lista deudas pendientes donde el usuario es deudor.

        Args:
            user_id: UUID del usuario deudor.

        Returns:
            Lista de deudas pendientes ordenadas por fecha de creación (más recientes primero).
        """
        stmt = (
            select(Debt)
            .where(
                Debt.debtor_id == user_id,
                Debt.status == DebtStatus.PENDING,
                Debt.deleted_at.is_(None),
            )
            .options(joinedload(Debt.shared_expense))
            .order_by(Debt.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, id: uuid.UUID) -> Debt | None:
        """Obtiene una deuda por ID con su gasto compartido asociado cargado."""
        stmt = (
            select(Debt)
            .where(Debt.id == id, Debt.deleted_at.is_(None))
            .options(joinedload(Debt.shared_expense))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_couple(self, couple_id: uuid.UUID) -> list[Debt]:
        """Lista todas las deudas de una pareja (historial completo).

        Hace JOIN con SharedExpense para filtrar por couple_id.

        Args:
            couple_id: UUID de la pareja.

        Returns:
            Lista de todas las deudas de la pareja ordenadas por fecha.
        """
        from app.models.shared_expense import SharedExpense

        stmt = (
            select(Debt)
            .join(SharedExpense, Debt.shared_expense_id == SharedExpense.id)
            .where(
                SharedExpense.couple_id == couple_id,
                Debt.deleted_at.is_(None),
            )
            .options(joinedload(Debt.shared_expense))
            .order_by(Debt.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_by_debtor_creditor(
        self, debtor_id: uuid.UUID, creditor_id: uuid.UUID
    ) -> list[Debt]:
        """Lista deudas pendientes entre un deudor y un acreedor específicos.

        Args:
            debtor_id: UUID del deudor.
            creditor_id: UUID del acreedor.

        Returns:
            Lista de deudas pendientes entre ambos.
        """
        stmt = select(Debt).where(
            Debt.debtor_id == debtor_id,
            Debt.creditor_id == creditor_id,
            Debt.status == DebtStatus.PENDING,
            Debt.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_total_owed_to_user(
        self, user_id: uuid.UUID, *, pending_only: bool = True
    ) -> Decimal:
        """Calcula cuánto le deben al usuario (como acreedor).

        Args:
            user_id: UUID del usuario acreedor.
            pending_only: Si True, solo suma deudas pendientes.

        Returns:
            Total adeudado al usuario como Decimal.
        """
        filters = [
            Debt.creditor_id == user_id,
            Debt.deleted_at.is_(None),
        ]
        if pending_only:
            filters.append(Debt.status == DebtStatus.PENDING)

        from sqlalchemy import func

        stmt = select(func.coalesce(func.sum(Debt.amount), 0)).where(*filters)
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))

    async def get_total_user_owes(
        self, user_id: uuid.UUID, *, pending_only: bool = True
    ) -> Decimal:
        """Calcula cuánto debe el usuario (como deudor).

        Args:
            user_id: UUID del usuario deudor.
            pending_only: Si True, solo suma deudas pendientes.

        Returns:
            Total que debe el usuario como Decimal.
        """
        filters = [
            Debt.debtor_id == user_id,
            Debt.deleted_at.is_(None),
        ]
        if pending_only:
            filters.append(Debt.status == DebtStatus.PENDING)

        from sqlalchemy import func

        stmt = select(func.coalesce(func.sum(Debt.amount), 0)).where(*filters)
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))
