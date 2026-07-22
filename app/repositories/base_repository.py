"""
Repository base genérico.

Implementa operaciones CRUD comunes con Soft Delete, para que los
repositorios concretos solo agreguen las consultas específicas de
su dominio (Documento 06 — Patrón Repository).
"""
import uuid
from datetime import datetime, timezone
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        stmt = select(self.model).where(
            self.model.id == id, self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def soft_delete(self, obj: ModelType) -> None:
        obj.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, obj: ModelType) -> None:
        await self.session.refresh(obj)
