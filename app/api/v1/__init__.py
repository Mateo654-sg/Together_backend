"""
Agrega todos los routers del módulo v1 bajo un único APIRouter.
"""
from fastapi import APIRouter

from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.budgets import router as budgets_router
from app.api.v1.categories import router as categories_router
from app.api.v1.chat import router as chat_router
from app.api.v1.couples import router as couples_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.debts import router as debts_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.goals import router as goals_router
from app.api.v1.incomes import router as incomes_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.reminders import router as reminders_router
from app.api.v1.reports import router as reports_router
from app.api.v1.shared_expenses import router as shared_expenses_router
from app.api.v1.shared_incomes import router as shared_incomes_router
from app.api.v1.statistics import router as statistics_router
from app.api.v1.users import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(ai_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(users_router)
api_router.include_router(couples_router)
api_router.include_router(dashboard_router)
api_router.include_router(budgets_router)
api_router.include_router(categories_router)
api_router.include_router(expenses_router)
api_router.include_router(goals_router)
api_router.include_router(incomes_router)
api_router.include_router(notifications_router)
api_router.include_router(reminders_router)
api_router.include_router(reports_router)
api_router.include_router(shared_expenses_router)
api_router.include_router(shared_incomes_router)
api_router.include_router(statistics_router)
api_router.include_router(debts_router)
