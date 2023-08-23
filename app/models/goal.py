from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator

from sqlalchemy import ForeignKey, String, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from .base import Base
from .user import User
from .target import Target


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
    user_id: Mapped[int] = mapped_column(
        "user_id", ForeignKey("user.id"), nullable=False
    )
    user: Mapped[User] = relationship("User", back_populates="goals")
