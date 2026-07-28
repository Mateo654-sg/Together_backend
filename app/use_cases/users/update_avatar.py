"""
Use Case: UpdateAvatar (FR-007, FR-124).

Actualiza la URL del avatar del usuario.
En el futuro se integrará con S3 para subir imágenes.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UpdateAvatarUseCase:
    """Use Case: UpdateAvatar (FR-007, FR-124).

    Actualiza la URL del avatar del usuario.
    En el futuro se integrará con S3 para subir imágenes.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(self, user_id: uuid.UUID, avatar_url: str) -> User:
        """Actualiza el avatar del usuario.

        Args:
            user_id: UUID del usuario.
            avatar_url: Nueva URL del avatar.

        Returns:
            El usuario con el avatar actualizado.

        Raises:
            NotFoundException: Si el usuario no existe.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")

        user.avatar_url = avatar_url
        await self.session.commit()
        return user
