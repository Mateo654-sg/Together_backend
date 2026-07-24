"""
Use Case: ListCategories.

Lista todas las categorías personales del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_category import PersonalCategory
from app.repositories.personal_category_repository import PersonalCategoryRepository


class ListCategoriesUseCase:
    """Use Case: ListCategories.

    Lista todas las categorías personales del usuario.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalCategoryRepository(session)

    async def execute(self, user_id: uuid.UUID) -> list[PersonalCategory]:
        """Lista todas las categorías personales del usuario.

        Args:
            user_id: UUID del usuario propietario.

        Returns:
            Lista de categorías personales ordenadas alfabéticamente.
        """
        return await self.repository.list_by_user(user_id)
