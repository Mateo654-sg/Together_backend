import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.personal_income import PersonalIncome
from app.repositories.personal_income_repository import PersonalIncomeRepository


class GetIncomeUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PersonalIncomeRepository(session)

    async def execute(self, user_id: uuid.UUID, income_id: uuid.UUID) -> PersonalIncome:
        income = await self.repository.get_by_user_and_id(user_id, income_id)
        if income is None:
            raise NotFoundException("Ingreso no encontrado.")
        return income
