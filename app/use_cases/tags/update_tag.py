"""
Use Case: UpdateTag (FR-026).

Edita una etiqueta de gasto del usuario.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.expense_tag import ExpenseTag
from app.repositories.expense_tag_repository import ExpenseTagRepository
from app.schemas.tag import UpdateTagRequest


class UpdateTagUseCase:
    """Use Case: UpdateTag (FR-026)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ExpenseTagRepository(session)

    async def execute(
        self, user_id: uuid.UUID, tag_id: uuid.UUID, data: UpdateTagRequest
    ) -> ExpenseTag:
        """Edita una etiqueta de gasto.

        Args:
            user_id: UUID del usuario propietario.
            tag_id: UUID de la etiqueta a editar.
            data: Datos a actualizar (name, color).

        Returns:
            La etiqueta actualizada.

        Raises:
            NotFoundException: Si la etiqueta no existe o no pertenece al usuario.
            ConflictException: Si el nuevo nombre ya lo usa otra etiqueta.
        """
        tag = await self.repository.get_by_user_and_id(user_id, tag_id)
        if tag is None:
            raise NotFoundException("Etiqueta no encontrada.")

        payload = data.model_dump(exclude_unset=True)

        if "name" in payload and payload["name"] is not None:
            new_name = payload["name"].strip()
            stmt = select(ExpenseTag).where(
                ExpenseTag.user_id == user_id,
                ExpenseTag.deleted_at.is_(None),
                ExpenseTag.name == new_name,
                ExpenseTag.id != tag_id,
            )
            existing = (await self.session.execute(stmt)).scalar_one_or_none()
            if existing is not None:
                raise ConflictException("Ya tienes una etiqueta con ese nombre.")
            tag.name = new_name

        if "color" in payload:
            tag.color = payload["color"]

        await self.session.commit()
        return tag
