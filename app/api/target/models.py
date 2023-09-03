from fastapi import HTTPException, status

from app.api.goal.utils import check_access_to_goal

from app.db import AsyncSession
from app.models import Goal, Target, TargetSchema


class AddTarget:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self, title: str, target: int, goal_id: int, user_id: int, progress: int
    ) -> TargetSchema:
        async with self.async_session.begin() as session:
            goal_instance = await Goal.read_by_id(session, goal_id)
            check_access_to_goal(goal_instance, user_id)

            target_instance = await Target.add(
                session, title, target, goal_id, progress
            )
            return TargetSchema.model_validate(target_instance)


class UpdateTarget:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self,
        goal_id: int,
        target_id: int,
        title: str,
        target: int,
        user_id: int,
        progress: int,
    ) -> TargetSchema:
        async with self.async_session.begin() as session:
            goal_instance = await Goal.read_by_id(session, goal_id)
            check_access_to_goal(goal_instance, user_id)

            target_instance = await Target.read_by_id(session, target_id)
            if not target_instance or target_instance.goal_id != goal_id:
                raise HTTPException(status.HTTP_404_NOT_FOUND)

            await target_instance.update(session, title, target, progress)
            await session.refresh(target_instance)
            return TargetSchema.model_validate(target_instance)


class DeleteTarget:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, goal_id: int, target_id: int, user_id: int) -> None:
        async with self.async_session.begin() as session:
            goal_instance = await Goal.read_by_id(session, goal_id)
            check_access_to_goal(goal_instance, user_id)

            target_instance = await Target.read_by_id(session, target_id)
            if not target_instance:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            await Target.delete(session, target_instance)
