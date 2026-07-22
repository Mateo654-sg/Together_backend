"""
Use Case: ChangePassword (FR-125).

Permite al usuario cambiar su contraseña verificando la actual.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsException, NotFoundException
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository


class ChangePasswordUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(
        self, user_id: uuid.UUID, current_password: str, new_password: str
    ) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")

        if not user.password_hash or not verify_password(
            current_password, user.password_hash
        ):
            raise InvalidCredentialsException("Contraseña actual incorrecta.")

        user.password_hash = hash_password(new_password)
        await self.session.commit()
