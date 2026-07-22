"""
Use Case: ListSharedIncomes.

Lista ingresos compartidos de la pareja.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.couple import CoupleStatus
from app.repositories.couple_repository import CoupleRepository
from app.repositories.shared_income_repository import SharedIncomeRepository
from app.schemas.shared_finance import SharedIncomeListResponse


class ListSharedIncomesUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.income_repository = SharedIncomeRepository(session)
        self.couple_repository = CoupleRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> SharedIncomeListResponse:
        couple = await self.couple_repository.get_active_for_user(user_id)
        if couple is None or couple.status != CoupleStatus.ACCEPTED:
            raise ConflictException("No tienes una pareja vinculada.")

        items, total = await self.income_repository.list_by_couple(
            couple.id, page=page, limit=limit
        )

        pages = max(1, -(-total // limit))

        return SharedIncomeListResponse(
            data=items,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": pages,
            },
        )
