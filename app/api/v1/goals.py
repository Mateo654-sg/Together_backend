"""
Router: /api/v1/goals

Metas compartidas de la pareja (FR-061 a FR-072).
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.goal import GoalStatus
from app.models.user import User
from app.schemas.goal import (
    ContributionListResponse,
    ContributionResponse,
    CreateContributionRequest,
    CreateGoalRequest,
    GoalListResponse,
    GoalResponse,
    GoalStatisticsResponse,
    UpdateGoalRequest,
)
from app.use_cases.goals.contribute_to_goal import ContributeToGoalUseCase
from app.use_cases.goals.create_goal import CreateGoalUseCase
from app.use_cases.goals.delete_goal import DeleteGoalUseCase
from app.use_cases.goals.get_goal_statistics import GetGoalStatisticsUseCase
from app.use_cases.goals.list_goal_history import ListGoalHistoryUseCase
from app.use_cases.goals.list_goals import ListGoalsUseCase
from app.use_cases.goals.update_goal import UpdateGoalUseCase

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.get("", response_model=GoalListResponse)
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: GoalStatus | None = Query(None, alias="status"),
):
    """FR-061: Lista todas las metas de la pareja."""
    use_case = ListGoalsUseCase(db)
    return await use_case.execute(
        current_user.id, page=page, limit=limit, status=status_filter
    )


@router.post(
    "", response_model=GoalResponse, status_code=status.HTTP_201_CREATED
)
async def create_goal(
    data: CreateGoalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-061: Crea una nueva meta compartida."""
    use_case = CreateGoalUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: uuid.UUID,
    data: UpdateGoalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-062: Editar una meta existente."""
    use_case = UpdateGoalUseCase(db)
    return await use_case.execute(current_user.id, goal_id, data)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-063: Eliminar una meta (soft delete)."""
    use_case = DeleteGoalUseCase(db)
    await use_case.execute(current_user.id, goal_id)


@router.post(
    "/contribute",
    response_model=ContributionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def contribute_to_goal(
    data: CreateContributionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-067: Registrar un aporte a una meta."""
    use_case = ContributeToGoalUseCase(db)
    return await use_case.execute(current_user.id, data)


@router.get("/history", response_model=ContributionListResponse)
async def list_goal_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """FR-067-List: Historial de aportes a metas."""
    use_case = ListGoalHistoryUseCase(db)
    return await use_case.execute(current_user.id, page=page, limit=limit)


@router.get("/statistics", response_model=GoalStatisticsResponse)
async def get_goal_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FR-069 a FR-072: Estadísticas generales de metas."""
    use_case = GetGoalStatisticsUseCase(db)
    return await use_case.execute(current_user.id)
