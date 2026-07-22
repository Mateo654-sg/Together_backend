"""
Use Case: RefreshToken.

Implementa rotación de Refresh Tokens (Documento 12 — Seguridad):
cada Refresh Token utilizado genera uno nuevo y el anterior queda
invalidado inmediatamente.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as app_settings
from app.core.exceptions import InvalidTokenException
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.session import Session as SessionModel
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RefreshRequest, TokenResponse


class RefreshTokenUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_repository = SessionRepository(session)
        self.user_repository = UserRepository(session)

    async def execute(self, data: RefreshRequest) -> TokenResponse:
        payload = decode_token(data.refresh_token, expected_type=TokenType.REFRESH)
        jti = payload.get("jti")
        user_id = payload.get("sub")

        session_obj = await self.session_repository.get_by_jti(jti)
        if session_obj is None or not self.session_repository.is_valid(session_obj):
            raise InvalidTokenException("La sesión ya no es válida.")

        user = await self.user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidTokenException()

        # Rotación: invalidar el token actual y emitir uno nuevo
        await self.session_repository.revoke(session_obj)

        new_access_token, _ = create_access_token(str(user.id))
        new_refresh_token, new_jti = create_refresh_token(str(user.id))

        new_session = SessionModel(
            user_id=user.id,
            refresh_token_jti=new_jti,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=app_settings.refresh_token_expire_days),
            device=session_obj.device,
            ip=session_obj.ip,
        )
        self.session.add(new_session)
        await self.session.commit()

        return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)
