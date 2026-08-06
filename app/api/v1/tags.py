"""
Router: /api/v1/tags

Etiquetas de gastos personales (FR-026).
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.tag import (
    CreateTagRequest,
    TagListResponse,
    TagResponse,
    UpdateTagRequest,
)
from app.use_cases.tags import (
    CreateTagUseCase,
    DeleteTagUseCase,
    ListTagsUseCase,
    UpdateTagUseCase,
)

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=TagListResponse)
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """FR-026: Lista las etiquetas del usuario."""
    use_case = ListTagsUseCase(db)
    return await use_case.execute(current_user.id, page=page, limit=limit)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: CreateTagRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-026: Crea una etiqueta de gasto."""
    use_case = CreateTagUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: uuid.UUID,
    data: UpdateTagRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-026: Edita una etiqueta de gasto."""
    use_case = UpdateTagUseCase(db)
    return await use_case.execute(current_user.id, tag_id, data)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-026: Elimina una etiqueta de gasto (soft delete)."""
    use_case = DeleteTagUseCase(db)
    await use_case.execute(current_user.id, tag_id)
