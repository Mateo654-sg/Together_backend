"""
Use Case: RegisterUser (FR-001).

Crea una nueva cuenta de usuario mediante correo electrónico.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EmailAlreadyExistsException
from app.core.security import hash_password
from app.models.user import User
from app.models.user_settings import UserSettings
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


class RegisterUserUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(self, data: RegisterRequest) -> User:
        email_normalized = data.email.lower()

        if await self.user_repository.email_exists(email_normalized):
            raise EmailAlreadyExistsException()

        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=email_normalized,
            password_hash=hash_password(data.password),
            is_verified=False,
        )
        await self.user_repository.create(user)

        # Crear configuración por defecto (Tabla 2 — user_settings)
        settings_obj = UserSettings(user_id=user.id)
        self.session.add(settings_obj)

        await self.session.commit()
        await self.user_repository.refresh(user)

        # TODO: disparar evento para enviar correo de verificación (FR-*)
        return user
