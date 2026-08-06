"""
Use Case: RevokeSession (FR-126).

Revoca una sesión específica del usuario.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.session import Session
from app.repositories.session_repository import SessionRepository


class RevokeSessionUseCase:
    """Use Case: RevokeSession (FR-126).

    Revoca una sesión del usuario (cierra la sesión de un dispositivo).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_repository = SessionRepository(session)

    async def execute(self, user_id: uuid.UUID, session_id: uuid.UUID) -> None:
        """Revoca la sesión indicada si pertenece al usuario.

        Args:
            user_id: UUID del usuario propietario.
            session_id: UUID de la sesión a revocar.

        Raises:
            NotFoundException: Si la sesión no existe o no pertenece al usuario.
        """
        stmt = select(Session).where(
            Session.id == session_id,
            Session.user_id == user_id,
            Session.deleted_at.is_(None),
        )
        session_obj = (await self.session.execute(stmt)).scalar_one_or_none()
        if session_obj is None:
            raise NotFoundException("La sesión no existe.")
        await self.session_repository.revoke(session_obj)
        await self.session.commit()
