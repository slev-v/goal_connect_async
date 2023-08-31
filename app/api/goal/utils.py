from fastapi import HTTPException, status
from app.models.goal import Goal


def check_access_to_goal(goal_instance: Goal | None, user_id: int) -> None:
    if not goal_instance:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if goal_instance.user_id != user_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You can't modify goals that you haven't created",
        )
