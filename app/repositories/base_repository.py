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
    """Repository base genérico con operaciones CRUD comunes.

    Implementa las operaciones básicas de acceso a datos con Soft Delete,
    para que los repositorios concretos solo agreguen las consultas
    específicas de su dominio.

    Args:
        session: Sesión async de SQLAlchemy.
        model: Clase del modelo ORM asociado a este repository.

    Type Parameters:
        ModelType: Tipo del modelo ORM que maneja el repository.
    """

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        """Obtiene un registro por su ID, excluyendo registros eliminados lógicamente.

        Args:
            id: UUID del registro a buscar.

        Returns:
            La instancia del modelo o None si no existe o fue eliminado.
        """
        stmt = select(self.model).where(
            self.model.id == id, self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, obj: ModelType) -> ModelType:
        """Inserta un nuevo registro en la base de datos.

        Args:
            obj: Instancia del modelo a crear.

        Returns:
            La misma instancia con el ID asignado.
        """
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def soft_delete(self, obj: ModelType) -> None:
        """Marca un registro como eliminado lógicamente (soft delete).

        No elimina el registro físicamente, solo establece deleted_at.

        Args:
            obj: Instancia del modelo a eliminar.
        """
        obj.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def commit(self) -> None:
        """Persiste los cambios acumulados en la sesión."""
        await self.session.commit()

    async def refresh(self, obj: ModelType) -> None:
        """Refresca el estado de una instancia desde la base de datos.

        Útil después de un create para obtener valores generados
        por el servidor (timestamps, etc.).

        Args:
            obj: Instancia a refrescar.
        """
        await self.session.refresh(obj)
