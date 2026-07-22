"""
Router: /api/v1/categories

Categorías personales para clasificar gastos e ingresos (FR-024).
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.personal_finance import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from app.use_cases.personal_finance.create_category import CreateCategoryUseCase
from app.use_cases.personal_finance.delete_category import DeleteCategoryUseCase
from app.use_cases.personal_finance.list_categories import ListCategoriesUseCase
from app.use_cases.personal_finance.update_category import UpdateCategoryUseCase

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas las categorías personales del usuario autenticado."""
    use_case = ListCategoriesUseCase(db)
    return await use_case.execute(current_user.id)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CreateCategoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-024: Crea una categoría personal nueva."""
    use_case = CreateCategoryUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    data: UpdateCategoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-024: Actualiza una categoría personal existente."""
    use_case = UpdateCategoryUseCase(db)
    return await use_case.execute(current_user.id, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-024: Elimina una categoría personal (soft delete)."""
    use_case = DeleteCategoryUseCase(db)
    await use_case.execute(current_user.id, category_id)
