from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .goal import Goal


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    email: Mapped[str] = mapped_column("email", nullable=False, unique=True)
    username: Mapped[str] = mapped_column("username", nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", server_default=func.now(), nullable=False
    )
    password: Mapped[str] = mapped_column("password", nullable=False)
    goals: Mapped[list[Goal]] = relationship(
        "Goal",
        back_populates="user",
        order_by="Goal.id",
        cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )

    @classmethod
    async def read_by_id(cls, session: AsyncSession, user_id: int) -> User | None:
        stmt = select(cls).where(cls.id == user_id)
        return await session.scalar(stmt.order_by(cls.id))

    @classmethod
    async def read_by_email_or_username(
        cls, session: AsyncSession, email: str, username: str
    ) -> User | None:
        stmt = select(cls).where((cls.username == username) | (cls.email == email))
        return await session.scalar(stmt)

    @classmethod
    async def read_by_username(
        cls, session: AsyncSession, username: str
    ) -> User | None:
        stmt = select(cls).where(cls.username == username)
        return await session.scalar(stmt)

    @classmethod
    async def delete_user(cls, session: AsyncSession, username: str) -> None:
        stmt = delete(cls).where(cls.username == username)
        await session.execute(stmt)

    @classmethod
    async def create(
        cls, session: AsyncSession, email: str, username: str, password: str
    ) -> User:
        user = User(email=email, username=username, password=password)
        session.add(user)
        await session.flush()

        new = await cls.read_by_id(session, user.id)
        if not new:
            raise RuntimeError()
        return new
