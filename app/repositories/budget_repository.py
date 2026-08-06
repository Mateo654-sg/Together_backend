"""
Repository de Budget (Tabla 14 — Documento 07).

Encapsula las consultas de presupuestos.
"""

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.budget import Budget
from app.repositories.base_repository import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    """Repository para el modelo Budget.

    Encapsula las consultas de presupuestos personales del usuario,
    incluyendo filtrado por mes/año/categoría y generación de alertas
    de gasto.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Budget)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        month: int | None = None,
        year: int | None = None,
        category_id: uuid.UUID | None = None,
    ) -> tuple[list[Budget], int]:
        """Lista presupuestos del usuario con filtros y paginación.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página (comienza en 1).
            limit: Cantidad máxima de resultados por página.
            month: Filtrar por mes específico (1-12).
            year: Filtrar por año específico.
            category_id: Filtrar por categoría específica.

        Returns:
            Tupla con la lista de presupuestos y el total de registros.
        """
        base_filter = [
            Budget.user_id == user_id,
            Budget.deleted_at.is_(None),
        ]

        if month is not None:
            base_filter.append(Budget.month == month)
        if year is not None:
            base_filter.append(Budget.year == year)
        if category_id is not None:
            base_filter.append(Budget.category_id == category_id)

        count_stmt = select(func.count()).select_from(Budget).where(*base_filter)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Budget)
            .options(selectinload(Budget.category))
            .where(*base_filter)
            .order_by(Budget.year.desc(), Budget.month.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user_and_id(
        self, user_id: uuid.UUID, budget_id: uuid.UUID
    ) -> Budget | None:
        """Obtiene un presupuesto verificando que pertenezca al usuario.

        Args:
            user_id: UUID del usuario propietario.
            budget_id: UUID del presupuesto a buscar.

        Returns:
            El presupuesto encontrado o None si no existe o no pertenece al usuario.
        """
        stmt = select(Budget).options(selectinload(Budget.category)).where(
            Budget.id == budget_id,
            Budget.user_id == user_id,
            Budget.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_category_month(
        self,
        user_id: uuid.UUID,
        category_id: uuid.UUID,
        month: int,
        year: int,
    ) -> Budget | None:
        """Obtiene el presupuesto del usuario para una categoría, mes y año específicos.

        Args:
            user_id: UUID del usuario.
            category_id: UUID de la categoría.
            month: Mes del presupuesto (1-12).
            year: Año del presupuesto.

        Returns:
            El presupuesto encontrado o None si no existe.
        """
        stmt = select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.month == month,
            Budget.year == year,
            Budget.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_alerts(
        self,
        user_id: uuid.UUID,
        *,
        month: int | None = None,
        year: int | None = None,
    ) -> list[dict]:
        """Genera alertas de presupuesto cuando se supera el umbral de gasto.

        Evalúa cada presupuesto y clasifica el nivel de alerta:
        - warning: 80% o más del presupuesto utilizado
        - critical: 90% o más del presupuesto utilizado
        - exceeded: 100% o más del presupuesto utilizado

        Args:
            user_id: UUID del usuario.
            month: Filtrar alertas por mes específico.
            year: Filtrar alertas por año específico.

        Returns:
            Lista de diccionarios con la información de cada alerta,
            incluyendo budget_id, category_id, amount, spent, percentage,
            level, month y year.
        """
        from app.models.personal_expense import PersonalExpense
        from sqlalchemy import extract

        budgets, _ = await self.list_by_user(
            user_id, page=1, limit=1000, month=month, year=year
        )
        if not budgets:
            return []

        category_filter = [
            b.category_id for b in budgets if b.category_id is not None
        ]
        months = {b.month for b in budgets if b.month}
        years = {b.year for b in budgets if b.year}

        expense_filter = [
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        ]
        if category_filter:
            expense_filter.append(
                PersonalExpense.category_id.in_(category_filter)
            )
        if months and years:
            expense_filter.append(
                extract("month", PersonalExpense.expense_date).in_(months)
            )
            expense_filter.append(
                extract("year", PersonalExpense.expense_date).in_(years)
            )

        spent_stmt = select(
            PersonalExpense.category_id,
            extract("month", PersonalExpense.expense_date).label("month"),
            extract("year", PersonalExpense.expense_date).label("year"),
            func.coalesce(func.sum(PersonalExpense.amount), 0).label("total"),
        ).where(*expense_filter).group_by(
            PersonalExpense.category_id,
            extract("month", PersonalExpense.expense_date),
            extract("year", PersonalExpense.expense_date),
        )

        spent_result = await self.session.execute(spent_stmt)
        spent_map: dict[tuple, Decimal] = {}
        for row in spent_result:
            key = (row.category_id, int(row.month), int(row.year))
            spent_map[key] = Decimal(str(row.total))

        alerts = []
        for budget in budgets:
            if budget.amount <= 0:
                continue

            key = (budget.category_id, budget.month, budget.year)
            spent = spent_map.get(key, Decimal("0"))

            percentage = float(spent / budget.amount * 100)

            if percentage >= 100:
                level = "exceeded"
            elif percentage >= 90:
                level = "critical"
            elif percentage >= 80:
                level = "warning"
            else:
                continue

            alerts.append(
                {
                    "budget_id": budget.id,
                    "category_id": budget.category_id,
                    "category_name": budget.category.name if budget.category else None,
                    "amount": budget.amount,
                    "spent": spent,
                    "percentage": min(percentage, 100.0),
                    "level": level,
                    "month": budget.month,
                    "year": budget.year,
                }
            )

        return alerts
