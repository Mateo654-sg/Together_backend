"""
Use Case: LogoutUser (FR-005).

Invalida la sesión (refresh token) asociada.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenType, decode_token
from app.repositories.session_repository import SessionRepository
from app.schemas.auth import RefreshRequest


class LogoutUserUseCase:
    """Use Case: LogoutUser (FR-005).

    Invalida la sesión (refresh token) asociada al usuario.
    La operación es idempotente: si el token ya es inválido, no retorna error.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_repository = SessionRepository(session)

    async def execute(self, data: RefreshRequest) -> None:
        """Ejecuta el logout invalidando el refresh token.

        Args:
            data: Datos con el refresh token a invalidar.
        """
        try:
            payload = decode_token(data.refresh_token, expected_type=TokenType.REFRESH)
        except Exception:
            # Logout es idempotente: si el token ya es inválido, no es un error.
            return

        jti = payload.get("jti")
        session_obj = await self.session_repository.get_by_jti(jti)
        if session_obj is not None:
            await self.session_repository.revoke(session_obj)
            await self.session.commit()
