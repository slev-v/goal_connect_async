from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .goal import Goal


class Target(Base):
    __tablename__ = "target"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    title: Mapped[str] = mapped_column("title", nullable=False)
    target: Mapped[int] = mapped_column("target", nullable=False)
    goal_id: Mapped[int] = mapped_column(
        "goal_id", ForeignKey("goal.id"), nullable=False
    )
    goal: Mapped[Goal] = relationship("Goal", back_populates="targets")

    @classmethod
    async def read_by_id(cls, session: AsyncSession, id: int) -> Target | None:
        stmt = select(cls).where(cls.id == id)
        return await session.scalar(stmt.order_by(cls.id))

    @classmethod
    async def add(
        cls, session: AsyncSession, title: str, target: int, goal_id: int
    ) -> Target:
        target_cls = Target(title=title, target=target, goal_id=goal_id)
        session.add(target_cls)
        await session.flush()

        new = await cls.read_by_id(session, target_cls.id)
        if not new:
            raise RuntimeError
        return new

    @classmethod
    async def delete(cls, session: AsyncSession, target: Target) -> None:
        await session.delete(target)
        await session.flush()

    async def update(self, session: AsyncSession, title: str, target: int) -> None:
        self.title = title
        self.target = target
        await session.flush()
