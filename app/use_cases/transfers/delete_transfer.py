"""
Use Case: DeleteTransfer (FR-021).

Elimina (soft delete) una transferencia del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.transfer_repository import TransferRepository


class DeleteTransferUseCase:
    """Use Case: DeleteTransfer (FR-021)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TransferRepository(session)

    async def execute(self, user_id: uuid.UUID, transfer_id: uuid.UUID) -> None:
        """Elimina una transferencia del usuario.

        Args:
            user_id: UUID del usuario propietario.
            transfer_id: UUID de la transferencia a eliminar.

        Raises:
            NotFoundException: Si la transferencia no existe o no pertenece al usuario.
        """
        transfer = await self.repository.get_by_user_and_id(user_id, transfer_id)
        if transfer is None:
            raise NotFoundException("Transferencia no encontrada.")

        await self.repository.soft_delete(transfer)
        await self.session.commit()
