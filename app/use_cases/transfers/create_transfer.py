"""
Use Case: CreateTransfer (FR-021).

Registra una transferencia entre métodos de pago del usuario.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.transfer import Transfer
from app.repositories.transfer_repository import TransferRepository
from app.schemas.transfer import CreateTransferRequest


class CreateTransferUseCase:
    """Use Case: CreateTransfer (FR-021)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TransferRepository(session)

    async def execute(
        self, user_id: uuid.UUID, data: CreateTransferRequest
    ) -> Transfer:
        """Registra una transferencia entre métodos de pago.

        Args:
            user_id: UUID del usuario propietario.
            data: Datos de la transferencia (from_method, to_method, amount, etc.).

        Returns:
            La transferencia creada.

        Raises:
            ValidationException: Si el método de origen y destino son iguales.
        """
        if data.from_method == data.to_method:
            raise ValidationException(
                "El método de origen y destino deben ser diferentes."
            )

        transfer = Transfer(
            user_id=user_id,
            from_method=data.from_method,
            to_method=data.to_method,
            amount=data.amount,
            description=data.description,
            transfer_date=data.transfer_date,
        )
        await self.repository.create(transfer)
        await self.session.commit()
        return transfer
