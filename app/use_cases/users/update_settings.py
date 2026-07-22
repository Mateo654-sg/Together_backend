"""
Use Case: UpdateSettings (FR-127, FR-128, FR-129).

Actualiza la configuración del usuario (tema, idioma, moneda, etc.).
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.user_settings import UserSettings
from app.repositories.user_repository import UserRepository
from app.schemas.user import UpdateUserSettingsRequest


class UpdateSettingsUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: UpdateUserSettingsRequest
    ) -> UserSettings:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Usuario no encontrado.")

        if user.settings is None:
            settings = UserSettings(user_id=user_id)
            self.session.add(settings)
            await self.session.flush()
            user.settings = settings

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user.settings, field, value)

        await self.session.commit()
        await self.session.refresh(user.settings)
        return user.settings
