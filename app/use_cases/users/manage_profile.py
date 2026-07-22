"""
Use Cases del módulo Users: consultar y editar perfil (FR-006).
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UpdateUserRequest


class GetCurrentUserUseCase:
    def __init__(self, session: AsyncSession):
        self.user_repository = UserRepository(session)

    async def execute(self, user_id) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")
        return user


class UpdateUserProfileUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(self, user_id, data: UpdateUserRequest) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.user_repository.refresh(user)
        return user


class DeleteUserUseCase:
    """Eliminación de cuenta (FR-010): Soft Delete tras confirmar contraseña."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(self, user_id, password: str) -> None:
        from app.core.exceptions import InvalidCredentialsException
        from app.core.security import verify_password

        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")

        if not user.password_hash or not verify_password(password, user.password_hash):
            raise InvalidCredentialsException("Contraseña incorrecta.")

        await self.user_repository.soft_delete(user)
        await self.session.commit()
