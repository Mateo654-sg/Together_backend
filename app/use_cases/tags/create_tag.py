"""
Use Case: CreateTag (FR-026).

Crea una etiqueta de gasto para el usuario.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.expense_tag import ExpenseTag
from app.repositories.expense_tag_repository import ExpenseTagRepository
from app.schemas.tag import CreateTagRequest


class CreateTagUseCase:
    """Use Case: CreateTag (FR-026)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ExpenseTagRepository(session)

    async def execute(self, user_id: uuid.UUID, data: CreateTagRequest) -> ExpenseTag:
        """Crea una etiqueta de gasto.

        Args:
            user_id: UUID del usuario propietario.
            data: Datos de la etiqueta (name, color).

        Returns:
            La etiqueta creada.

        Raises:
            ConflictException: Si el usuario ya tiene una etiqueta con ese nombre.
        """
        stmt = select(ExpenseTag).where(
            ExpenseTag.user_id == user_id,
            ExpenseTag.deleted_at.is_(None),
            ExpenseTag.name == data.name.strip(),
        )
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing is not None:
            raise ConflictException("Ya tienes una etiqueta con ese nombre.")

        tag = ExpenseTag(
            user_id=user_id,
            name=data.name.strip(),
            color=data.color,
        )
        await self.repository.create(tag)
        await self.session.commit()
        return tag
