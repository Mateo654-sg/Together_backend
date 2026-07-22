"""
Import centralizado de todos los modelos ORM.

Necesario para que Alembic detecte automáticamente los modelos
al generar migraciones (autogenerate).
"""
from app.db.base import Base  # noqa: F401
from app.models.ai_history import AIHistory  # noqa: F401
from app.models.budget import Budget  # noqa: F401
from app.models.couple import Couple  # noqa: F401
from app.models.debt import Debt  # noqa: F401
from app.models.goal import Goal  # noqa: F401
from app.models.goal_contribution import GoalContribution  # noqa: F401
from app.models.login_history import LoginHistory  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.personal_category import PersonalCategory  # noqa: F401
from app.models.personal_expense import PersonalExpense  # noqa: F401
from app.models.personal_income import PersonalIncome  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.reminder import Reminder  # noqa: F401
from app.models.session import Session  # noqa: F401
from app.models.shared_category import SharedCategory  # noqa: F401
from app.models.shared_expense import SharedExpense  # noqa: F401
from app.models.shared_income import SharedIncome  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_settings import UserSettings  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401

__all__ = [
    "Base",
    "AIHistory",
    "User",
    "UserSettings",
    "Couple",
    "Budget",
    "Session",
    "LoginHistory",
    "Notification",
    "Reminder",
    "PersonalCategory",
    "PersonalExpense",
    "PersonalIncome",
    "Report",
    "SharedCategory",
    "SharedExpense",
    "SharedIncome",
    "Debt",
    "Goal",
    "GoalContribution",
    "ChatMessage",
]
