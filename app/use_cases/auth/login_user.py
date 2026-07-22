"""
Use Case: LoginUser (FR-002).

Valida credenciales, gestiona bloqueo por intentos fallidos
(Documento 12: 5 intentos → bloqueo de 15 minutos) y emite tokens.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AccountLockedException, InvalidCredentialsException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.models.session import Session as SessionModel
from app.repositories.login_history_repository import LoginHistoryRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class LoginUserUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.session_repository = SessionRepository(session)
        self.login_history_repository = LoginHistoryRepository(session)

    async def execute(
        self, data: LoginRequest, ip: str | None = None, device: str | None = None
    ) -> TokenResponse:
        user = await self.user_repository.get_by_email(data.email)

        if user is None:
            await self.login_history_repository.record(
                data.email, success=False, ip=ip, device=device, reason="user_not_found"
            )
            await self.session.commit()
            raise InvalidCredentialsException()

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedException()

        if not user.password_hash or not verify_password(data.password, user.password_hash):
            await self.user_repository.increment_failed_attempts(user)
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=LOCKOUT_MINUTES
                )
            await self.login_history_repository.record(
                data.email,
                success=False,
                user_id=user.id,
                ip=ip,
                device=device,
                reason="invalid_password",
            )
            await self.session.commit()
            raise InvalidCredentialsException()

        # Login exitoso: resetear intentos fallidos
        await self.user_repository.reset_failed_attempts(user)
        user.last_login = datetime.now(timezone.utc)

        access_token, _ = create_access_token(str(user.id))
        refresh_token, refresh_jti = create_refresh_token(str(user.id))

        from app.core.config import settings as app_settings

        session_obj = SessionModel(
            user_id=user.id,
            refresh_token_jti=refresh_jti,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=app_settings.refresh_token_expire_days),
            device=device,
            ip=ip,
        )
        self.session.add(session_obj)

        await self.login_history_repository.record(
            data.email, success=True, user_id=user.id, ip=ip, device=device
        )
        await self.session.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
