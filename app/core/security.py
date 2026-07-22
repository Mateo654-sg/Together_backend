"""
Seguridad: hashing de contraseñas y manejo de JWT.

Sigue los lineamientos del Documento 12 — Seguridad:
- Hash de contraseñas con Argon2id (memory_cost=64MB, iterations=4, parallelism=2)
- Access Token: 15 minutos
- Refresh Token: 30 días, con rotación (el anterior se invalida al usarse)
"""
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import InvalidTokenException

# Argon2id según configuración mínima del Documento 12
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=4,  # iterations
    argon2__parallelism=2,
)


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def hash_password(password: str) -> str:
    """Genera el hash Argon2id de una contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    extra_claims: dict | None = None,
) -> tuple[str, str]:
    """
    Crea un JWT firmado.

    Retorna (token, jti) — el jti (JWT ID) se usa para poder invalidar
    tokens específicos (p. ej. en logout o rotación de refresh tokens).
    """
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    payload = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti,
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti


def create_access_token(user_id: str) -> tuple[str, str]:
    """Crea un Access Token de corta duración (15 minutos por defecto)."""
    return _create_token(
        subject=user_id,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """Crea un Refresh Token de larga duración (30 días por defecto)."""
    return _create_token(
        subject=user_id,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: TokenType) -> dict:
    """
    Decodifica y valida un JWT.

    Lanza InvalidTokenException si el token es inválido, expiró,
    o no corresponde al tipo esperado (access vs refresh).
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        raise InvalidTokenException()

    if payload.get("type") != expected_type.value:
        raise InvalidTokenException("Tipo de token incorrecto.")

    return payload
