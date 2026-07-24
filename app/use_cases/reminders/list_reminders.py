"""
Use Case: ListReminders (FR-109-List).

Lista los recordatorios del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.reminder_repository import ReminderRepository
from app.schemas.reminder import ReminderListResponse, ReminderResponse


class ListRemindersUseCase:
    """Use Case: ListReminders (FR-109-List).

    Lista los recordatorios del usuario con filtros y paginación.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.reminder_repository = ReminderRepository(session)

    async def execute(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        limit: int = 20,
        completed: bool | None = None,
    ) -> ReminderListResponse:
        """Lista recordatorios del usuario.

        Args:
            user_id: UUID del usuario propietario.
            page: Número de página.
            limit: Cantidad máxima de resultados.
            completed: Filtrar por estado de completado.

        Returns:
            ReminderListResponse con recordatorios y paginación.
        """
        reminders, total = await self.reminder_repository.list_by_user(
            user_id, page=page, limit=limit, completed=completed
        )

        data = [ReminderResponse.model_validate(r) for r in reminders]

        return ReminderListResponse(
            data=data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
            },
        )
