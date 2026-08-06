"""
Use Case: UpdateTransfer (FR-021).

Edita una transferencia existente del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.transfer import Transfer
from app.repositories.transfer_repository import TransferRepository
from app.schemas.transfer import UpdateTransferRequest


class UpdateTransferUseCase:
    """Use Case: UpdateTransfer (FR-021)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TransferRepository(session)

    async def execute(
        self, user_id: uuid.UUID, transfer_id: uuid.UUID, data: UpdateTransferRequest
    ) -> Transfer:
        """Edita una transferencia del usuario.

        Args:
            user_id: UUID del usuario propietario.
            transfer_id: UUID de la transferencia a editar.
            data: Datos a actualizar.

        Returns:
            La transferencia actualizada.

        Raises:
            NotFoundException: Si la transferencia no existe o no pertenece al usuario.
            ValidationException: Si los métodos de origen y destino quedan iguales.
        """
        transfer = await self.repository.get_by_user_and_id(user_id, transfer_id)
        if transfer is None:
            raise NotFoundException("Transferencia no encontrada.")

        payload = data.model_dump(exclude_unset=True)

        if "from_method" in payload and payload["from_method"] is not None:
            transfer.from_method = payload["from_method"]
        if "to_method" in payload and payload["to_method"] is not None:
            transfer.to_method = payload["to_method"]

        if transfer.from_method == transfer.to_method:
            raise ValidationException(
                "El método de origen y destino deben ser diferentes."
            )

        if "amount" in payload and payload["amount"] is not None:
            transfer.amount = payload["amount"]
        if "description" in payload:
            transfer.description = payload["description"]
        if "transfer_date" in payload and payload["transfer_date"] is not None:
            transfer.transfer_date = payload["transfer_date"]

        await self.session.commit()
        return transfer
