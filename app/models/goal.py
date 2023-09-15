from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from .base import Base
from .target import Target

if TYPE_CHECKING:
    from .user import User


class Goal(Base):
    __tablename__ = "goal"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    title: Mapped[str] = mapped_column("title", nullable=False)
    description: Mapped[str] = mapped_column("description")
    private: Mapped[bool] = mapped_column("private", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", server_default=func.now(), nullable=False
    )
    targets: Mapped[list[Target]] = relationship(
        "Target",
        back_populates="goal",
        order_by="Target.id",
        cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    user_id: Mapped[int] = mapped_column("user_id", ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship("User", back_populates="goals")

    @classmethod
    async def read_by_id(cls, session: AsyncSession, id: int) -> Goal | None:
        stmt = select(cls).where(cls.id == id).options(selectinload(cls.targets))
        return await session.scalar(stmt.order_by(cls.id))

    @classmethod
    async def read_user_goals(
        cls, session: AsyncSession, user_id: int, limit: int, offset: int
    ) -> AsyncIterator[Goal]:
        stmt = (
            select(cls)
            .where(cls.user_id == user_id)
            .limit(limit)
            .offset(offset)
            .options(selectinload(cls.targets))
        )
        stream = await session.stream_scalars(stmt.order_by(cls.id))
        async for row in stream:
            yield row

    @classmethod
    async def read_public_goals(
        cls, session: AsyncSession, limit: int, offset: int
    ) -> AsyncIterator[Goal]:
        stmt = (
            select(cls)
            .where(cls.private == False)
            .limit(limit)
            .offset(offset)
            .options(selectinload(cls.targets))
        )
        stream = await session.stream_scalars(stmt.order_by(cls.id))
        async for row in stream:
            yield row

    @classmethod
    async def add_goal(
        cls,
        session: AsyncSession,
        title: str,
        description: str,
        private: bool,
        user_id: int,
        targets: list[Target],
    ) -> Goal:
        goal = Goal(
            title=title,
            description=description,
            private=private,
            user_id=user_id,
        )
        session.add(goal)
        for target in targets:
            target = Target(
                title=target.title,
                target=target.target,
                goal=goal,
                progress=target.progress,
            )
            session.add(target)
        await session.flush()

        new = await cls.read_by_id(session, goal.id)
        if not new:
            raise RuntimeError()
        return new

    async def update(
        self, session: AsyncSession, title: str, description: str, private: bool
    ) -> None:
        self.title = title
        self.description = description
        self.private = private
        await session.flush()

    @classmethod
    async def delete(cls, session: AsyncSession, goal: Goal) -> None:
        await session.delete(goal)
        await session.flush()
