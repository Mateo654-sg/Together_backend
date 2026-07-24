"""
Use Case: ListIncomes.

Lista ingresos personales con soporte para filtros y paginación.
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.schemas.personal_finance import IncomeListResponse


class ListIncomesUseCase:
    """Use Case: ListIncomes.

    Lista ingresos personales con soporte para filtros y paginación.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalIncomeRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> IncomeListResponse:
        """Lista ingresos personales con filtros y paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.
            category_id: Filtrar por categoría específica.
            date_from: Fecha de inicio del rango.
            date_to: Fecha de fin del rango.

        Returns:
            IncomeListResponse con los ingresos y datos de paginación.
        """
        items, total = await self.repository.list_by_user(
            user_id,
            page=page,
            limit=limit,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
        )

        pages = max(1, -(-total // limit))

        return IncomeListResponse(
            data=items,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": pages,
            },
        )
