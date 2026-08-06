"""
Use Case: ExportUserData (FR-130).

Retorna los datos del usuario en un archivo ZIP para portabilidad:
perfil, configuración, parejas, movimientos personales y compartidos,
deudas, metas, presupuestos, tags y recordatorios.
"""
import io
import json
import uuid
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.couple import Couple
from app.models.debt import Debt
from app.models.expense_tag import ExpenseTag
from app.models.goal import Goal
from app.models.personal_expense import PersonalExpense
from app.models.personal_income import PersonalIncome
from app.models.reminder import Reminder
from app.models.shared_expense import SharedExpense
from app.models.shared_income import SharedIncome
from app.models.user import User
from app.models.user_settings import UserSettings


@dataclass
class ExportResult:
    """Contenido de archivo exportado listo para responder."""

    content: bytes
    media_type: str
    filename: str


def _to_serializable(value):
    """Convierte valores ORM/Python a tipos JSON-serializables."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_to_serializable(item) for item in value]
    return str(value)


def _model_to_dict(model) -> dict | None:
    """Serializa un modelo SQLAlchemy a un dict plano JSON-serializable."""
    if model is None:
        return None
    return {
        column: _to_serializable(getattr(model, column))
        for column in model.__table__.columns.keys()
    }


class ExportUserDataUseCase:
    """FR-130: Exporta los datos del usuario como ZIP (JSON)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _query_all(self, model, *filters) -> list:
        stmt = select(model).where(*filters).order_by(model.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def execute(self, user_id: uuid.UUID) -> ExportResult:
        """Reúne y empaqueta todos los datos del usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            ExportResult con un ZIP que contiene together_export.json.
        """
        user = await self.session.get(User, user_id)

        settings = (
            await self.session.execute(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
        ).scalar_one_or_none()

        expenses = await self._query_all(
            PersonalExpense,
            PersonalExpense.user_id == user_id,
            PersonalExpense.deleted_at.is_(None),
        )
        incomes = await self._query_all(
            PersonalIncome,
            PersonalIncome.user_id == user_id,
            PersonalIncome.deleted_at.is_(None),
        )
        tags = await self._query_all(
            ExpenseTag, ExpenseTag.user_id == user_id, ExpenseTag.deleted_at.is_(None)
        )
        reminders = await self._query_all(
            Reminder, Reminder.user_id == user_id, Reminder.deleted_at.is_(None)
        )
        budgets = await self._query_all(
            Budget, Budget.user_id == user_id, Budget.deleted_at.is_(None)
        )
        personal_goals = await self._query_all(
            Goal, Goal.user_id == user_id, Goal.deleted_at.is_(None)
        )

        couples = await self._query_all(
            Couple,
            or_(
                Couple.partner_one_id == user_id,
                Couple.partner_two_id == user_id,
            ),
        )
        couple_ids = [couple.id for couple in couples]

        shared_expenses: list = []
        shared_incomes: list = []
        couple_goals: list = []
        debts: list = []
        if couple_ids:
            shared_expenses = await self._query_all(
                SharedExpense, SharedExpense.couple_id.in_(couple_ids)
            )
            shared_incomes = await self._query_all(
                SharedIncome, SharedIncome.couple_id.in_(couple_ids)
            )
            couple_goals = await self._query_all(
                Goal, Goal.couple_id.in_(couple_ids), Goal.deleted_at.is_(None)
            )
            debts = await self._query_all(
                Debt, Debt.shared_expense_id.in_([e.id for e in shared_expenses])
            )

        data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "profile": _model_to_dict(user),
            "settings": _model_to_dict(settings),
            "couples": [_model_to_dict(c) for c in couples],
            "expenses": [_model_to_dict(e) for e in expenses],
            "incomes": [_model_to_dict(i) for i in incomes],
            "shared_expenses": [_model_to_dict(e) for e in shared_expenses],
            "shared_incomes": [_model_to_dict(i) for i in shared_incomes],
            "debts": [_model_to_dict(d) for d in debts],
            "goals": [
                _model_to_dict(g) for g in [*personal_goals, *couple_goals]
            ],
            "budgets": [_model_to_dict(b) for b in budgets],
            "tags": [_model_to_dict(t) for t in tags],
            "reminders": [_model_to_dict(r) for r in reminders],
        }

        payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("together_export.json", payload)

        return ExportResult(
            content=buffer.getvalue(),
            media_type="application/zip",
            filename=(
                f"together-data-{datetime.now(timezone.utc).date().isoformat()}.zip"
            ),
        )
