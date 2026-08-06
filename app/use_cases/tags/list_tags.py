"""
Use Case: ListTags (FR-026).

Lista las etiquetas de gastos del usuario con paginación.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.expense_tag_repository import ExpenseTagRepository
from app.schemas.tag import TagListResponse


class ListTagsUseCase:
    """Use Case: ListTags (FR-026)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ExpenseTagRepository(session)

    async def execute(
        self, user_id: uuid.UUID, *, page: int = 1, limit: int = 20
    ) -> TagListResponse:
        """Lista las etiquetas del usuario con paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.

        Returns:
            TagListResponse con las etiquetas y datos de paginación.
        """
        items, total = await self.repository.list_by_user(
            user_id, page=page, limit=limit
        )

        pages = max(1, -(-total // limit))

        return TagListResponse(
            data=items,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": pages,
            },
        )
