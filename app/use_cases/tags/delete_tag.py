"""
Use Case: DeleteTag (FR-026).

Elimina (soft delete) una etiqueta de gasto y desvincula sus relaciones.
"""

import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.expense_tag import expense_tag_relation
from app.repositories.expense_tag_repository import ExpenseTagRepository


class DeleteTagUseCase:
    """Use Case: DeleteTag (FR-026)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ExpenseTagRepository(session)

    async def execute(self, user_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        """Elimina una etiqueta de gasto.

        Args:
            user_id: UUID del usuario propietario.
            tag_id: UUID de la etiqueta a eliminar.

        Raises:
            NotFoundException: Si la etiqueta no existe o no pertenece al usuario.
        """
        tag = await self.repository.get_by_user_and_id(user_id, tag_id)
        if tag is None:
            raise NotFoundException("Etiqueta no encontrada.")

        await self.session.execute(
            delete(expense_tag_relation).where(expense_tag_relation.c.tag_id == tag_id)
        )
        await self.repository.soft_delete(tag)
        await self.session.commit()
