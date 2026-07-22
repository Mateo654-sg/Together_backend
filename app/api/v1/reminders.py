"""
Router: /api/v1/reminders

Recordatorios financieros (FR-109 a FR-113).
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.reminder import (
    CreateReminderRequest,
    ReminderListResponse,
    ReminderResponse,
    UpdateReminderRequest,
)
from app.use_cases.reminders.complete_reminder import CompleteReminderUseCase
from app.use_cases.reminders.create_reminder import CreateReminderUseCase
from app.use_cases.reminders.delete_reminder import DeleteReminderUseCase
from app.use_cases.reminders.list_reminders import ListRemindersUseCase
from app.use_cases.reminders.update_reminder import UpdateReminderUseCase

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get("", response_model=ReminderListResponse)
async def list_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    completed: bool | None = Query(None),
):
    """FR-109: Lista recordatorios con filtros."""
    use_case = ListRemindersUseCase(db)
    return await use_case.execute(
        current_user.id, page=page, limit=limit, completed=completed
    )


@router.post(
    "", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED
)
async def create_reminder(
    data: CreateReminderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-109: Crea un nuevo recordatorio."""
    use_case = CreateReminderUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: uuid.UUID,
    data: UpdateReminderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-110: Editar un recordatorio existente."""
    use_case = UpdateReminderUseCase(db)
    return await use_case.execute(current_user.id, reminder_id, data)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-111: Eliminar un recordatorio (soft delete)."""
    use_case = DeleteReminderUseCase(db)
    await use_case.execute(current_user.id, reminder_id)


@router.patch("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marcar recordatorio como completado."""
    use_case = CompleteReminderUseCase(db)
    return await use_case.execute(current_user.id, reminder_id)
