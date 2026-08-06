"""
Use Case: GetTransfer (FR-021).

Obtiene una transferencia específica del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.transfer import Transfer
from app.repositories.transfer_repository import TransferRepository


class GetTransferUseCase:
    """Use Case: GetTransfer (FR-021)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TransferRepository(session)

    async def execute(
        self, user_id: uuid.UUID, transfer_id: uuid.UUID
    ) -> Transfer:
        """Obtiene una transferencia del usuario.

        Args:
            user_id: UUID del usuario propietario.
            transfer_id: UUID de la transferencia a buscar.

        Returns:
            La transferencia encontrada.

        Raises:
            NotFoundException: Si la transferencia no existe o no pertenece al usuario.
        """
        transfer = await self.repository.get_by_user_and_id(user_id, transfer_id)
        if transfer is None:
            raise NotFoundException("Transferencia no encontrada.")
        return transfer
