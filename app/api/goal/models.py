from typing import AsyncIterator, List

from fastapi import HTTPException, status

from app.api.goal.utils import check_access_to_goal

from .schemas import TargetRequest
from app.db import AsyncSession
from app.models import Goal, GoalSchema, Target, TargetSchema, User


class CreateGoal:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self,
        title: str,
        description: str,
        private: bool,
        targets: list[TargetRequest],
        user_id: int,
    ) -> GoalSchema:
        async with self.async_session.begin() as session:
            goal = await Goal.add_goal(
                session, title, description, private, user_id, targets
            )
            return GoalSchema.model_validate(goal)


class ReadGoal:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, goal_id: int, user_id: int) -> GoalSchema:
        async with self.async_session() as session:
            goal = await Goal.read_by_id(session, goal_id)
            if not goal:
                raise HTTPException(status.HTTP_404_NOT_FOUND)

            if goal.user_id != user_id and goal.private:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN,
                    detail="You can't read goal that you haven't created",
                )
            return GoalSchema.model_validate(goal)


class ReadUserGoals:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self, user_id: int, limit: int, offset: int
    ) -> AsyncIterator[GoalSchema]:
        async with self.async_session() as session:
            async for goal in Goal.read_user_goals(session, user_id, limit, offset):
                yield GoalSchema.model_validate(goal)


class AddTargetToGoal:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self, title: str, target: int, goal_id: int, user_id: int
    ) -> TargetSchema:
        async with self.async_session.begin() as session:
            goal_instance = await Goal.read_by_id(session, goal_id)
            check_access_to_goal(goal_instance, user_id)

            target_instance = await Target.add(session, title, target, goal_id)
            return TargetSchema.model_validate(target_instance)


class DeleteGoal:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, id: int, user_id: int) -> None:
        async with self.async_session.begin() as session:
            goal = await Goal.read_by_id(session, id)
            check_access_to_goal(goal, user_id)
            await Goal.delete(session, goal)  # type: ignore


class UpdateGoal:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self,
        id: int,
        title: str,
        description: str,
        private: bool,
        user_id: int,
    ) -> GoalSchema:
        async with self.async_session.begin() as session:
            goal = await Goal.read_by_id(session, id)
            check_access_to_goal(goal, user_id)

            await goal.update(session, title, description, private)  # type: ignore
            await session.refresh(goal)
            return GoalSchema.model_validate(goal)


class UpdateTarget:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self, goal_id: int, target_id: int, title: str, target: int, user_id: int
    ) -> TargetSchema:
        async with self.async_session.begin() as session:
            goal_instance = await Goal.read_by_id(session, goal_id)
            check_access_to_goal(goal_instance, user_id)

            target_instance = await Target.read_by_id(session, target_id)
            if not target_instance or target_instance.goal_id != goal_id:
                raise HTTPException(status.HTTP_404_NOT_FOUND)

            await target_instance.update(session, title, target)
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
                return
            await Target.delete(session, target_instance)
