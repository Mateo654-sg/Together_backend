"""
Repository de Couple (Tabla 3 — Documento 07).

Reglas de negocio que este repository ayuda a garantizar:
- No permitir una pareja con más de dos integrantes (solo dos columnas FK).
- Un usuario solo puede tener una relación activa (pending/accepted) a la vez.
"""
import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.couple import Couple, CoupleStatus
from app.repositories.base_repository import BaseRepository

ACTIVE_STATUSES = (CoupleStatus.PENDING, CoupleStatus.ACCEPTED)


class CoupleRepository(BaseRepository[Couple]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Couple)

    async def get_active_for_user(self, user_id: uuid.UUID) -> Couple | None:
        """Retorna la relación activa (pending o accepted) de un usuario, si existe."""
        stmt = select(Couple).where(
            or_(Couple.partner_one_id == user_id, Couple.partner_two_id == user_id),
            Couple.status.in_(ACTIVE_STATUSES),
            Couple.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_invitation_code(self, code: str) -> Couple | None:
        stmt = select(Couple).where(
            Couple.invitation_code == code, Couple.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def code_exists(self, code: str) -> bool:
        return await self.get_by_invitation_code(code) is not None
