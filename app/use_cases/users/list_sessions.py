"""
Use Case: ListSessionHistory (FR-126).

Consulta el historial de sesiones del usuario.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.schemas.user import SessionHistoryItem, SessionHistoryResponse


class ListSessionHistoryUseCase:
    """Use Case: ListSessionHistory (FR-126).

    Consulta el historial de sesiones del usuario (últimas 20).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, user_id: uuid.UUID) -> SessionHistoryResponse:
        """Lista el historial de sesiones del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            SessionHistoryResponse con las últimas 20 sesiones.
        """
        stmt = (
            select(Session)
            .where(Session.user_id == user_id, Session.deleted_at.is_(None))
            .order_by(Session.created_at.desc())
            .limit(20)
        )
        result = await self.session.execute(stmt)
        sessions = list(result.scalars().all())

        data = [
            SessionHistoryItem(
                id=s.id,
                device=s.device,
                ip=s.ip,
                is_revoked=s.is_revoked,
                created_at=s.created_at,
                expires_at=s.expires_at,
            )
            for s in sessions
        ]

        return SessionHistoryResponse(data=data)
