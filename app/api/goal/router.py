from typing import Annotated
from fastapi import APIRouter, Depends, Query, status

from .schemas import (
    AllGoalsWithTargetResponse,
    GoalWithTargetRequest,
    GoalRequest,
    GoalWithTargetResponse,
    AllGoalsSchemaResponse,
)
from .models import (
    CreateGoal,
    ReadGoal,
    ReadPublicGoals,
    ReadUserGoals,
    DeleteGoal,
    UpdateGoal,
)
from app.models.schema import GoalSchema, UserSchema
from app.api.user.jwt import (
    get_current_user_from_token,
    optional_get_current_user_from_token,
)

router = APIRouter(prefix="/goal", tags=["goal"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=GoalWithTargetResponse
)
async def add_goal(
    data: GoalWithTargetRequest,
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)],
    use_case: CreateGoal = Depends(CreateGoal),
) -> GoalSchema:
    return await use_case.execute(
        data.title, data.description, data.private, data.targets, current_user.id
    )


@router.get("", response_model=AllGoalsWithTargetResponse)
async def get_user_goals(
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    use_case: ReadUserGoals = Depends(ReadUserGoals),
) -> AllGoalsSchemaResponse:
    return AllGoalsSchemaResponse(
        goals=[goal async for goal in use_case.execute(current_user.id, limit, offset)]
    )


@router.get("/public", response_model=AllGoalsWithTargetResponse)
async def get_public_goals(
    offset: int = 0,
    limit: int = 10,
    use_case: ReadPublicGoals = Depends(ReadPublicGoals),
) -> AllGoalsSchemaResponse:
    return AllGoalsSchemaResponse(
        goals=[goal async for goal in use_case.execute(limit, offset)]
    )


@router.get("/{goal_id}", response_model=GoalWithTargetResponse)
async def get_goal_by_id(
    goal_id: int,
    current_user: Annotated[UserSchema, Depends(optional_get_current_user_from_token)],
    use_case: ReadGoal = Depends(ReadGoal),
):
    if current_user:
        return await use_case.execute(goal_id, current_user.id)
    else:
        return await use_case.execute(goal_id)


@router.put("/{goal_id}", response_model=GoalWithTargetResponse)
async def update_goal(
    data: GoalRequest,
    goal_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)],
    use_case: UpdateGoal = Depends(UpdateGoal),
):
    return await use_case.execute(
        goal_id, data.title, data.description, data.private, current_user.id
    )


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)],
    use_case: DeleteGoal = Depends(DeleteGoal),
) -> None:
    return await use_case.execute(goal_id, current_user.id)
