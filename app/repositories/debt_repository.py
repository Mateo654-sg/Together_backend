"""
Repository de Debt (Tabla 10 — Documento 07).

Encapsula las consultas de deudas entre pareja.
"""
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.debt import Debt, DebtStatus
from app.repositories.base_repository import BaseRepository


class DebtRepository(BaseRepository[Debt]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Debt)

    async def list_pending_for_user(self, user_id: uuid.UUID) -> list[Debt]:
        """Deudas pendientes donde el usuario es deudor."""
        stmt = (
            select(Debt)
            .where(
                Debt.debtor_id == user_id,
                Debt.status == DebtStatus.PENDING,
                Debt.deleted_at.is_(None),
            )
            .order_by(Debt.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_couple(self, couple_id: uuid.UUID) -> list[Debt]:
        """Todas las deudas de una pareja (para historial)."""
        from app.models.shared_expense import SharedExpense

        stmt = (
            select(Debt)
            .join(SharedExpense, Debt.shared_expense_id == SharedExpense.id)
            .where(
                SharedExpense.couple_id == couple_id,
                Debt.deleted_at.is_(None),
            )
            .order_by(Debt.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_by_debtor_creditor(
        self, debtor_id: uuid.UUID, creditor_id: uuid.UUID
    ) -> list[Debt]:
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
        """Cuánto le deben al usuario (como acreedor)."""
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
        """Cuánto debe el usuario (como deudor)."""
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
