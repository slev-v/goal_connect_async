from __future__ import annotations

from enum import unique
from typing import TYPE_CHECKING, AsyncIterator

from sqlalchemy import ForeignKey, String, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

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
