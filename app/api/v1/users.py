"""
Router: /api/v1/users
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UpdateAvatarRequest,
    UpdateUserRequest,
    UpdateUserSettingsRequest,
    UserResponse,
    UserSettingsResponse,
    UserStatisticsResponse,
)
from app.use_cases.users.get_settings import GetSettingsUseCase
from app.use_cases.users.get_statistics import GetUserStatisticsUseCase
from app.use_cases.users.manage_profile import (
    DeleteUserUseCase,
    UpdateUserProfileUseCase,
)
from app.use_cases.users.update_avatar import UpdateAvatarUseCase
from app.use_cases.users.update_settings import UpdateSettingsUseCase
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retorna el perfil del usuario autenticado."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-006: Editar información personal."""
    use_case = UpdateUserProfileUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.delete("/me", status_code=204)
async def delete_me(
    password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-010: Eliminar cuenta (requiere confirmar contraseña)."""
    use_case = DeleteUserUseCase(db)
    await use_case.execute(current_user.id, password)


@router.get("/settings", response_model=UserSettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-127/FR-128/FR-129: Obtiene la configuración del usuario."""
    use_case = GetSettingsUseCase(db)
    return await use_case.execute(current_user.id)


@router.put("/settings", response_model=UserSettingsResponse)
async def update_settings(
    data: UpdateUserSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-127/FR-128/FR-129: Actualiza la configuración del usuario."""
    use_case = UpdateSettingsUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    data: UpdateAvatarRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-007/FR-124: Actualiza la foto de perfil del usuario."""
    use_case = UpdateAvatarUseCase(db)
    return await use_case.execute(current_user.id, data.avatar_url)


@router.get("/statistics", response_model=UserStatisticsResponse)
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna estadísticas personales del usuario."""
    use_case = GetUserStatisticsUseCase(db)
    return await use_case.execute(current_user.id)
