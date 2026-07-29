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
    """Extrae y valida el usuario actual desde el JWT Access Token.

    Decodifica el token Bearer, extrae el user_id del claim 'sub',
    y carga el usuario desde la base de datos.

    Args:
        credentials: Credenciales Bearer del header Authorization.
        db: Sesión de base de datos async.

    Returns:
        El usuario autenticado y activo.

    Raises:
        UnauthorizedException: Si no se proporciona token o el usuario no es válido.
        InvalidTokenException: Si el token es inválido o el user_id no es UUID válido.
    """
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

    if not user.is_verified:
        raise UnauthorizedException("Cuenta no verificada. Revisa tu correo electrónico.")

    return user


def get_client_ip(x_forwarded_for: str | None = Header(default=None)) -> str | None:
    """Extrae la IP del cliente, considerando proxys/load balancers.

    Args:
        x_forwarded_for: Header X-Forwarded-For (opcional).

    Returns:
        La IP del cliente o None si no está disponible.
    """
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return None


def get_device_info(user_agent: str | None = Header(default=None)) -> str | None:
    """Extrae la información del dispositivo/navegador desde User-Agent.

    Args:
        user_agent: Header User-Agent (opcional).

    Returns:
        La cadena del User-Agent o None si no está disponible.
    """
    return user_agent
