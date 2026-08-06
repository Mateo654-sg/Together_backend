import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class ForgotPasswordUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.token_repository = PasswordResetTokenRepository(session)

    async def execute(self, email: str) -> None:
        user = await self.user_repository.get_by_email(email)

        if user is None:
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        await self.token_repository.create(reset_token)
        await self.session.commit()

        logger.info(
            "Password reset token generated for %s. In production, send via email.",
            email,
        )
