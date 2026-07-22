"""
Use Case: GetSettings (FR-127, FR-128, FR-129).

Retorna la configuración del usuario. Si no existe, crea una
con los valores por defecto.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_settings import UserSettings
from app.repositories.user_repository import UserRepository


class GetSettingsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(self, user_id: uuid.UUID) -> UserSettings:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Usuario no encontrado.")

        if user.settings is None:
            settings = UserSettings(user_id=user_id)
            self.session.add(settings)
            await self.session.commit()
            await self.session.refresh(settings)
            return settings

        return user.settings
