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
    """Repository para el modelo Couple.

    Reglas de negocio que este repository ayuda a garantizar:
    - No permitir una pareja con más de dos integrantes (solo dos columnas FK).
    - Un usuario solo puede tener una relación activa (pending/accepted) a la vez.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Couple)

    async def get_active_for_user(self, user_id: uuid.UUID) -> Couple | None:
        """Retorna la relación activa (pending o accepted) de un usuario, si existe.

        Busca en ambas columnas partner_one_id y partner_two_id para
        encontrar la relación en la que participa el usuario.

        Args:
            user_id: UUID del usuario a buscar.

        Returns:
            La pareja activa o None si no tiene relación.
        """
        stmt = select(Couple).where(
            or_(Couple.partner_one_id == user_id, Couple.partner_two_id == user_id),
            Couple.status.in_(ACTIVE_STATUSES),
            Couple.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_invitation_code(self, code: str) -> Couple | None:
        """Busca una pareja por código de invitación.

        Args:
            code: Código de invitación de 8 caracteres.

        Returns:
            La pareja encontrada o None.
        """
        stmt = select(Couple).where(
            Couple.invitation_code == code, Couple.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def code_exists(self, code: str) -> bool:
        """Verifica si un código de invitación ya está en uso.

        Args:
            code: Código a verificar.

        Returns:
            True si el código ya existe, False de lo contrario.
        """
        return await self.get_by_invitation_code(code) is not None
