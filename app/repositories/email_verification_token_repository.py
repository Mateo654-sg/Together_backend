from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_verification_token import EmailVerificationToken


class EmailVerificationTokenRepository:
    """Repositorio para tokens de verificación de correo."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: EmailVerificationToken) -> EmailVerificationToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_token_hash(
        self, token_hash: str
    ) -> EmailVerificationToken | None:
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def mark_used(self, token: EmailVerificationToken) -> None:
        token.used = True
        token.used_at = datetime.now(timezone.utc)
        await self.session.flush()
