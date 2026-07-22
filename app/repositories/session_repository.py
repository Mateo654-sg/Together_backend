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
    def __init__(self, session: AsyncSession):
        super().__init__(session, Session)

    async def get_by_jti(self, jti: str) -> Session | None:
        stmt = select(Session).where(
            Session.refresh_token_jti == jti, Session.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, session_obj: Session) -> None:
        session_obj.is_revoked = True
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = select(Session).where(
            Session.user_id == user_id,
            Session.is_revoked.is_(False),
            Session.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        for s in result.scalars().all():
            s.is_revoked = True
        await self.session.flush()

    def is_valid(self, session_obj: Session) -> bool:
        return (
            not session_obj.is_revoked
            and session_obj.expires_at > datetime.now(timezone.utc)
        )
