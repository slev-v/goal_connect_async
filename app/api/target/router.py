from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.models.schema import UserSchema
from app.api.user.jwt import get_current_user_from_token

from .schemas import TargetResponse, TargetRequest
from .models import AddTarget, UpdateTarget, DeleteTarget

router = APIRouter(prefix="/target", tags=["target"])


@router.post("", response_model=TargetResponse)
async def add_target_to_goal(
    goal_id: int,
    data: TargetRequest,
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)],
    use_case: AddTarget = Depends(AddTarget),
) -> TargetResponse:
    target = await use_case.execute(
        data.title, data.target, goal_id, current_user.id, data.progress
    )
    return TargetResponse(
        title=target.title, target=target.target, id=target.id, progress=target.progress
    )


@router.put("/{target_id}", response_model=TargetResponse)
async def update_target(
    goal_id: int,
    target_id: int,
    data: TargetRequest,
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)],
    use_case: UpdateTarget = Depends(UpdateTarget),
) -> TargetResponse:
    target = await use_case.execute(
        goal_id, target_id, data.title, data.target, current_user.id, data.progress
    )
    return TargetResponse(
        title=target.title, target=target.target, id=target.id, progress=target.progress
    )


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    goal_id: int,
    target_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)],
    use_case: DeleteTarget = Depends(DeleteTarget),
) -> None:
    return await use_case.execute(goal_id, target_id, current_user.id)
