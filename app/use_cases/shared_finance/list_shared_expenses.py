"""
Use Case: ListSharedExpenses.

Lista gastos compartidos de la pareja con filtros y paginación.
"""
import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.shared_expense_repository import SharedExpenseRepository
from app.schemas.shared_finance import SharedExpenseListResponse


class ListSharedExpensesUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repository = SharedExpenseRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        category_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> SharedExpenseListResponse:
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        items, total = await self.expense_repository.list_by_couple(
            couple.id,
            page=page,
            limit=limit,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
        )

        pages = max(1, -(-total // limit))

        return SharedExpenseListResponse(
            data=items,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": pages,
            },
        )
