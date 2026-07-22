"""
Dependencias comunes de FastAPI.

get_current_user valida el JWT Access Token y carga el usuario.
Cada endpoint protegido debe usar esta dependencia — nunca confiar
en el Frontend para la autorización (Documento 12).
"""
import uuid

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenException, UnauthorizedException
from app.core.security import TokenType, decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedException("Se requiere autenticación.")

    payload = decode_token(credentials.credentials, expected_type=TokenType.ACCESS)
    user_id = payload.get("sub")

    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, TypeError):
        raise InvalidTokenException()

    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_uuid)

    if user is None or not user.is_active:
        raise UnauthorizedException("Usuario no válido.")

    return user


def get_client_ip(x_forwarded_for: str | None = Header(default=None)) -> str | None:
    """Extrae la IP del cliente, considerando proxys/load balancers."""
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return None


def get_device_info(user_agent: str | None = Header(default=None)) -> str | None:
    return user_agent
