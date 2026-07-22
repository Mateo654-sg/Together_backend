"""
Use Case: CreateCategory (FR-024).

Registra una categoría personal nueva para el usuario.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.personal_category import PersonalCategory
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.schemas.personal_finance import CreateCategoryRequest


class CreateCategoryUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalCategoryRepository(session)

    async def execute(self, user_id: uuid.UUID, data: CreateCategoryRequest) -> PersonalCategory:
        if await self.repository.name_exists_for_user(user_id, data.name):
            raise ConflictException("Ya existe una categoría con ese nombre.")

        category = PersonalCategory(
            user_id=user_id,
            name=data.name.strip(),
            icon=data.icon,
            color=data.color,
        )
        await self.repository.create(category)
        await self.session.commit()
        await self.repository.refresh(category)
        return category
