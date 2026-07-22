"""
Use Case: DeleteCategory (FR-024 — eliminación de categoría).

Elimina lógicamente (soft delete) una categoría personal.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.personal_category_repository import PersonalCategoryRepository


class DeleteCategoryUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalCategoryRepository(session)

    async def execute(self, user_id: uuid.UUID, category_id: uuid.UUID) -> None:
        category = await self.repository.get_by_user_and_id(user_id, category_id)
        if category is None:
            raise NotFoundException("Categoría no encontrada.")

        await self.repository.soft_delete(category)
        await self.session.commit()
