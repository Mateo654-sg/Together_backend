"""
Router: /api/v1/auth

Toda la lógica de negocio vive en los Use Cases. Este router
únicamente valida el request (vía Pydantic) y delega.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_device_info
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.use_cases.auth.login_user import LoginUserUseCase
from app.use_cases.auth.logout_user import LogoutUserUseCase
from app.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.use_cases.auth.register_user import RegisterUserUseCase

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """FR-001: Crear una cuenta mediante correo electrónico."""
    use_case = RegisterUserUseCase(db)
    user = await use_case.execute(data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    ip: str | None = Depends(get_client_ip),
    device: str | None = Depends(get_device_info),
):
    """FR-002: Iniciar sesión."""
    use_case = LoginUserUseCase(db)
    return await use_case.execute(data, ip=ip, device=device)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Renueva el Access Token mediante rotación de Refresh Token."""
    use_case = RefreshTokenUseCase(db)
    return await use_case.execute(data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """FR-005: Cerrar sesión."""
    use_case = LogoutUserUseCase(db)
    await use_case.execute(data)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(data: dict, db: AsyncSession = Depends(get_db)):
    """FR-003: Recuperar contraseña (envío de correo con token)."""
    # TODO: Implementar envío de correo con token de recuperación.
    # Se retorna 204 siempre, exista o no el correo, para evitar
    # enumeración de usuarios (buena práctica de seguridad).
    return None


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(data: dict, db: AsyncSession = Depends(get_db)):
    """FR-003: Restablecer contraseña mediante token."""
    # TODO: Implementar validación de token + actualización de password_hash.
    return None
