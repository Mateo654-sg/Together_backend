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
