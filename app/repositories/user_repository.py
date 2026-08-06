"""
Repository de User.

Encapsula todas las consultas relacionadas al modelo User.
Nunca se accede a la base de datos directamente desde services o use cases.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository para el modelo User.

    Encapsula todas las consultas relacionadas al modelo User.
    Nunca se accede a la base de datos directamente desde services
    o use cases, siempre a través de repositories.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_id(self, id: uuid.UUID) -> User | None:
        """Busca un usuario por ID con sus relaciones cargadas (async-safe).

        Carga la configuración (settings) de forma eager para evitar
        lazy loading en contexto async (MissingGreenlet).

        Args:
            id: UUID del usuario.

        Returns:
            El usuario encontrado o None.
        """
        stmt = (
            select(User)
            .where(User.id == id, User.deleted_at.is_(None))
            .options(selectinload(User.settings))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Busca un usuario por su correo electrónico (normalizado a minúsculas).

        Args:
            email: Correo electrónico a buscar.

        Returns:
            El usuario encontrado o None.
        """
        stmt = select(User).where(
            User.email == email.lower(), User.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> User | None:
        """Busca un usuario por su Google ID (OAuth).

        Args:
            google_id: ID único de Google del usuario.

        Returns:
            El usuario encontrado o None.
        """
        stmt = select(User).where(
            User.google_id == google_id, User.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Verifica si ya existe un usuario con el correo dado.

        Args:
            email: Correo electrónico a verificar.

        Returns:
            True si el correo ya está registrado, False de lo contrario.
        """
        user = await self.get_by_email(email)
        return user is not None

    async def increment_failed_attempts(self, user: User) -> None:
        """Incrementa el contador de intentos fallidos de login.

        Se usa para implementar el bloqueo tras 5 intentos fallidos
        (Documento 12 — Seguridad).

        Args:
            user: Usuario cuyo contador se incrementará.
        """
        user.failed_login_attempts += 1
        await self.session.flush()

    async def reset_failed_attempts(self, user: User) -> None:
        """Resetea los intentos fallidos y desbloquea la cuenta.

        Se llama después de un login exitoso.

        Args:
            user: Usuario a desbloquear.
        """
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.session.flush()
