"""
Repository de LoginHistory — registro de auditoría de accesos.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_history import LoginHistory


class LoginHistoryRepository:
    """Repository para el modelo LoginHistory.

    Registra intentos de login (exitosos y fallidos) para auditoría.
    No hereda de BaseRepository porque no necesita soft delete ni
    operaciones CRUD generales.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def record(
        self,
        email_attempted: str,
        success: bool,
        user_id=None,
        ip: str | None = None,
        device: str | None = None,
        reason: str | None = None,
    ) -> LoginHistory:
        """Registra un intento de acceso al sistema.

        Args:
            email_attempted: Correo electrónico intentado.
            success: True si el login fue exitoso, False si falló.
            user_id: UUID del usuario si el login fue exitoso, None en caso contrario.
            ip: Dirección IP del cliente (opcional).
            device: Información del dispositivo/navegador (opcional).
            reason: Razón del fallo cuando success=False (opcional).

        Returns:
            La entrada de LoginHistory creada.
        """
        entry = LoginHistory(
            user_id=user_id,
            email_attempted=email_attempted.lower(),
            success=success,
            ip=ip,
            device=device,
            reason=reason,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry
