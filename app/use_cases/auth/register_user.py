"""
Use Case: RegisterUser (FR-001).

Crea una nueva cuenta de usuario mediante correo electrónico y emite tokens.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as app_settings
from app.core.exceptions import EmailAlreadyExistsException
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.personal_category import PersonalCategory
from app.models.session import Session as SessionModel
from app.models.user import User
from app.models.user_settings import UserSettings
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, TokenResponse

DEFAULT_CATEGORIES = [
    ("Alimentación", "UtensilsCrossed", "#FF6B6B"),
    ("Transporte", "Car", "#4ECDC4"),
    ("Entretenimiento", "Gamepad2", "#A78BFA"),
    ("Servicios", "Wifi", "#F59E0B"),
    ("Salud", "Heart", "#EF4444"),
    ("Educación", "BookOpen", "#3B82F6"),
    ("Ropa", "Shirt", "#EC4899"),
    ("Otros", "MoreHorizontal", "#6B7280"),
    ("Salario", "Banknote", "#10B981"),
    ("Freelance", "Laptop", "#8B5CF6"),
    ("Inversiones", "TrendingUp", "#06B6D4"),
    ("Regalos", "Gift", "#F97316"),
]


class RegisterUserUseCase:
    """Use Case: RegisterUser (FR-001).

    Crea una nueva cuenta de usuario mediante correo electrónico,
    crea configuración por defecto (UserSettings), categorías por defecto
    y emite tokens JWT.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(
        self, data: RegisterRequest, ip: str | None = None, device: str | None = None
    ) -> TokenResponse:
        """Registra un nuevo usuario en el sistema y emite tokens.

        Args:
            data: Datos de registro (first_name, last_name, email, password).
            ip: Dirección IP del cliente (opcional).
            device: Información del dispositivo (opcional).

        Returns:
            TokenResponse con los tokens de acceso y refresh.

        Raises:
            EmailAlreadyExistsException: Si el correo ya está registrado.
        """
        email_normalized = data.email.lower()

        if await self.user_repository.email_exists(email_normalized):
            raise EmailAlreadyExistsException()

        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=email_normalized,
            password_hash=hash_password(data.password),
            is_verified=False,
        )
        await self.user_repository.create(user)

        # Crear configuración por defecto (Tabla 2 — user_settings)
        settings_obj = UserSettings(user_id=user.id)
        self.session.add(settings_obj)

        # Crear categorías por defecto
        for name, icon, color in DEFAULT_CATEGORIES:
            category = PersonalCategory(
                user_id=user.id,
                name=name,
                icon=icon,
                color=color,
            )
            await self.category_repository.create(category)

        # Emitir tokens JWT después del registro
        access_token, _ = create_access_token(str(user.id))
        refresh_token, refresh_jti = create_refresh_token(str(user.id))

        session_obj = SessionModel(
            user_id=user.id,
            refresh_token_jti=refresh_jti,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=app_settings.refresh_token_expire_days),
            device=device,
            ip=ip,
        )
        self.session.add(session_obj)

        await self.session.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
