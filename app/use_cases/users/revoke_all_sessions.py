"""
Use Case: RevokeAllSessions (FR-126).

Revoca todas las sesiones del usuario excepto la actual.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class RevokeAllSessionsUseCase:
    """Use Case: RevokeAllSessions (FR-126).

    Cierra la sesión de todos los dispositivos excepto el que realiza
    la petición (identificado por el JTI del refresh token).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, user_id: uuid.UUID, except_jti: str | None = None) -> int:
        """Revoca todas las sesiones activas del usuario excepto una.

        Args:
            user_id: UUID del usuario.
            except_jti: JTI de la sesión actual a conservar (opcional).

        Returns:
            Número de sesiones revocadas.
        """
        stmt = select(Session).where(
            Session.user_id == user_id,
            Session.is_revoked.is_(False),
            Session.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        count = 0
        for s in result.scalars().all():
            if except_jti and s.refresh_token_jti == except_jti:
                continue
            s.is_revoked = True
            count += 1
        await self.session.commit()
        return count
