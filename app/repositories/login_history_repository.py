"""
Repository de LoginHistory — registro de auditoría de accesos.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_history import LoginHistory


class LoginHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record(
        self,
        email_attempted: str,
        success: bool,
        user_id=None,
        ip: str | None = None,
        device: str | None = None,
        reason: str | None = None,
    ) -> LoginHistory:
        entry = LoginHistory(
            user_id=user_id,
            email_attempted=email_attempted.lower(),
            success=success,
            ip=ip,
            device=device,
            reason=reason,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry
