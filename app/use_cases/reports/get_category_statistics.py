"""
Use Case: GetCategoryStatistics (FR-091).

Obtiene estadísticas por categoría del usuario.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.personal_category import PersonalCategory
from app.models.personal_expense import PersonalExpense
from app.models.personal_income import PersonalIncome
from app.schemas.report import CategoryStatisticsResponse

UNCATEGORIZED_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")


class GetCategoryStatisticsUseCase:
    """Use Case: GetCategoryStatistics (FR-091).

    Obtiene estadísticas de gastos (o ingresos) agrupadas por categoría.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        month: int | None = None,
        year: int | None = None,
        type: str = "expense",
    ) -> list[CategoryStatisticsResponse]:
        """Calcula estadísticas por categoría del usuario.

        Args:
            user_id: UUID del usuario.
            month: Mes a consultar (opcional).
            year: Año a consultar (opcional).
            type: Tipo de movimiento (expense o income).

        Returns:
            Lista de CategoryStatisticsResponse ordenada por monto descendente.

        Raises:
            ValidationException: Si el tipo no es válido.
        """
        today = date.today()
        target_year = year or today.year
        target_month = month

        if type not in {"expense", "income"}:
            raise ValidationException("El tipo debe ser 'expense' o 'income'.")

        model = PersonalExpense if type == "expense" else PersonalIncome
        date_column = (
            PersonalExpense.expense_date if type == "expense" else PersonalIncome.income_date
        )

        filters = [
            model.user_id == user_id,
            model.deleted_at.is_(None),
            extract("year", date_column) == target_year,
        ]
        if target_month is not None:
            filters.append(extract("month", date_column) == target_month)

        stmt = (
            select(
                model.category_id,
                func.coalesce(PersonalCategory.name, "").label("category_name"),
                func.sum(model.amount).label("total"),
                func.count(model.id).label("count"),
            )
            .outerjoin(PersonalCategory, model.category_id == PersonalCategory.id)
            .where(*filters)
            .group_by(model.category_id, PersonalCategory.name)
            .order_by(func.sum(model.amount).desc())
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        total_stmt = (
            select(func.coalesce(func.sum(model.amount), 0))
            .where(*filters)
        )
        grand_total = Decimal(str((await self.session.execute(total_stmt)).scalar_one()))

        statistics = []
        for category_id, category_name, total, count in rows:
            cat_id = category_id if category_id is not None else UNCATEGORIZED_ID
            name = category_name or "Sin categoría"
            percentage = (
                float((Decimal(str(total)) / grand_total) * 100)
                if grand_total > 0
                else 0.0
            )
            statistics.append(
                CategoryStatisticsResponse(
                    category_id=cat_id,
                    category_name=name,
                    total_amount=Decimal(str(total)),
                    percentage_of_total=round(percentage, 2),
                    transaction_count=count,
                )
            )

        return statistics
