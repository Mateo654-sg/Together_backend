"""
Use Cases del módulo Users: consultar y editar perfil (FR-006).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsException, NotFoundException
from app.core.security import verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UpdateUserRequest


class GetCurrentUserUseCase:
    """Use Case: GetCurrentuser (FR-006).

    Consulta el perfil del usuario autenticado.
    """

    def __init__(self, session: AsyncSession):
        self.user_repository = UserRepository(session)

    async def execute(self, user_id) -> User:
        """Obtiene los datos del usuario actual.

        Args:
            user_id: UUID del usuario.

        Returns:
            El usuario encontrado.

        Raises:
            NotFoundException: Si el usuario no existe.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")
        return user


class UpdateUserProfileUseCase:
    """Use Case: UpdateUserProfile (FR-006).

    Actualiza el perfil del usuario autenticado.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(self, user_id, data: UpdateUserRequest) -> User:
        """Actualiza los datos del perfil del usuario.

        Args:
            user_id: UUID del usuario.
            data: Datos a actualizar (parciales).

        Returns:
            El usuario actualizado.

        Raises:
            NotFoundException: Si el usuario no existe.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        return user


class DeleteUserUseCase:
    """Use Case: DeleteUser (FR-010).

    Eliminación de cuenta: Soft Delete tras confirmar contraseña.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(self, user_id, password: str) -> None:
        """Elimina lógicamente la cuenta del usuario.

        Args:
            user_id: UUID del usuario.
            password: Contraseña para confirmar la eliminación.

        Raises:
            NotFoundException: Si el usuario no existe.
            InvalidCredentialsException: Si la contraseña es incorrecta.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")

        if not user.password_hash or not verify_password(password, user.password_hash):
            raise InvalidCredentialsException("Contraseña incorrecta.")

        await self.user_repository.soft_delete(user)
        await self.session.commit()
