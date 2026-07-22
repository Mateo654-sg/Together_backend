"""
Use Case: UpdateCategory (FR-024 — edición de categoría).

Actualiza el nombre, icono o color de una categoría existente.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.personal_category import PersonalCategory
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.schemas.personal_finance import UpdateCategoryRequest


class UpdateCategoryUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalCategoryRepository(session)

    async def execute(
        self, user_id: uuid.UUID, category_id: uuid.UUID, data: UpdateCategoryRequest
    ) -> PersonalCategory:
        category = await self.repository.get_by_user_and_id(user_id, category_id)
        if category is None:
            raise NotFoundException("Categoría no encontrada.")

        if data.name is not None and data.name != category.name:
            if await self.repository.name_exists_for_user(user_id, data.name):
                raise ConflictException("Ya existe una categoría con ese nombre.")
            category.name = data.name.strip()

        if data.icon is not None:
            category.icon = data.icon
        if data.color is not None:
            category.color = data.color

        await self.session.commit()
        await self.repository.refresh(category)
        return category
