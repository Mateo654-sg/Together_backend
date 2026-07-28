"""
Use Case: GoogleLogin.

Verifica un ID token de Google, crea o encuentra el usuario
y emite tokens de acceso/refresh.
"""

from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as app_settings
from app.core.security import create_access_token, create_refresh_token
from app.models.personal_category import PersonalCategory
from app.models.session import Session as SessionModel
from app.models.user import User
from app.models.user_settings import UserSettings
from app.repositories.personal_category_repository import PersonalCategoryRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import GoogleLoginRequest, TokenResponse

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

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class GoogleLoginUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.session_repository = SessionRepository(session)
        self.category_repository = PersonalCategoryRepository(session)

    async def execute(
        self, data: GoogleLoginRequest, ip: str | None = None, device: str | None = None
    ) -> TokenResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                GOOGLE_TOKENINFO_URL, params={"id_token": data.id_token}
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de Google inválido o expirado.",
            )

        info = resp.json()

        email = info.get("email")
        google_id = info.get("sub")
        first_name = info.get("given_name", "")
        last_name = info.get("family_name", "")
        avatar_url = info.get("picture")

        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token de Google no contiene los datos requeridos.",
            )

        user = await self.user_repository.get_by_google_id(google_id)
        if user is None:
            user = await self.user_repository.get_by_email(email)

        if user is None:
            user = User(
                first_name=first_name or "",
                last_name=last_name or "",
                email=email,
                google_id=google_id,
                avatar_url=avatar_url,
                is_verified=True,
            )
            self.session.add(user)
            await self.session.flush()

            settings_obj = UserSettings(user_id=user.id)
            self.session.add(settings_obj)

            for name, icon, color in DEFAULT_CATEGORIES:
                category = PersonalCategory(
                    user_id=user.id,
                    name=name,
                    icon=icon,
                    color=color,
                )
                await self.category_repository.create(category)
        else:
            if not user.google_id:
                user.google_id = google_id
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            if not user.is_verified:
                user.is_verified = True

        user.last_login = datetime.now(timezone.utc)

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
