"""
Repository de Session — maneja refresh tokens y sesiones activas.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repository para el modelo Session.

    Gestiona refresh tokens, revocación de sesiones y validación
    de sesiones activas. Las sesiones tienen un JTI único para
    cada refresh token.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Session)

    async def get_by_jti(self, jti: str) -> Session | None:
        """Obtiene una sesión por su JWT ID (JTI).

        Args:
            jti: Identificador único del JWT.

        Returns:
            La sesión encontrada o None si no existe.
        """
        stmt = select(Session).where(
            Session.refresh_token_jti == jti, Session.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, session_obj: Session) -> None:
        """Revoca una sesión específica (logout).

        Args:
            session_obj: Instancia de la sesión a revocar.
        """
        session_obj.is_revoked = True
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        """Revoca todas las sesiones activas de un usuario.

        Args:
            user_id: UUID del usuario cuyas sesiones serán revocadas.

        Returns:
            Número de sesiones revocadas.
        """
        stmt = select(Session).where(
            Session.user_id == user_id,
            Session.is_revoked.is_(False),
            Session.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        for s in result.scalars().all():
            s.is_revoked = True
        await self.session.flush()
        return result.rowcount

    def is_valid(self, session_obj: Session) -> bool:
        """Verifica si una sesión es válida.

        Una sesión es válida si no ha sido revocada y no ha expirado.

        Args:
            session_obj: Instancia de la sesión a validar.

        Returns:
            True si la sesión es válida, False de lo contrario.
        """
        return not session_obj.is_revoked and session_obj.expires_at > datetime.now(
            timezone.utc
        )
