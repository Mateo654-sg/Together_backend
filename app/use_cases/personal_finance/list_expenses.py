"""
Use Case: ListExpenses (FR-036, FR-037, FR-038, FR-039).

Lista gastos personales con soporte para filtros, búsqueda,
ordenamiento y paginación.
"""
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.schemas.personal_finance import ExpenseListResponse


class ListExpensesUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalExpenseRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        search: str | None = None,
        sort_by: str = "expense_date",
        sort_order: str = "desc",
    ) -> ExpenseListResponse:
        items, total = await self.repository.list_by_user(
            user_id,
            page=page,
            limit=limit,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        pages = max(1, -(-total // limit))  # ceil division

        return ExpenseListResponse(
            data=items,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": pages,
            },
        )
