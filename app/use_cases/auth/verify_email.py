"""
Use Case: VerifyEmail.

Verifica la cuenta de un usuario mediante un token de verificación
enviado tras el registro (flujo "Verificar correo" — Documento 05).
"""

import hashlib
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenException
from app.repositories.email_verification_token_repository import (
    EmailVerificationTokenRepository,
)
from app.repositories.user_repository import UserRepository


class VerifyEmailUseCase:
    """Use Case: VerifyEmail (verificar correo tras registro)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.token_repository = EmailVerificationTokenRepository(session)
        self.user_repository = UserRepository(session)

    async def execute(self, token: str) -> None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        verification_token = await self.token_repository.get_by_token_hash(token_hash)

        if verification_token is None or verification_token.used:
            raise InvalidTokenException()

        if verification_token.expires_at <= datetime.now(timezone.utc):
            raise InvalidTokenException()

        user = await self.user_repository.get_by_id(verification_token.user_id)
        if user is None:
            raise InvalidTokenException()

        user.is_verified = True
        await self.token_repository.mark_used(verification_token)
        await self.session.commit()
