from fastapi import HTTPException, status

from app.database.db import AsyncSession
from app.models import User, UserSchema

from .security import get_password_hash, verify_password


class ReadUserById:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, user_id: int) -> UserSchema:
        async with self.async_session() as session:
            user = await User.read_by_id(session, user_id)
            if not user:
                raise HTTPException(status.HTTP_404_NOT_FOUND)
            return UserSchema.model_validate(user)


class ReadUserByUsername:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, username: str) -> UserSchema:
        async with self.async_session() as session:
            user = await User.read_by_username(session, username)
            if not user:
                raise HTTPException(status.HTTP_404_NOT_FOUND)
            return UserSchema.model_validate(user)


class RegisterUser:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, email: str, username: str, password: str) -> UserSchema:
        async with self.async_session.begin() as session:
            uniq = await User.read_by_email_or_username(session, email, username)
            if uniq and uniq.email == email:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email is already taken")
            elif uniq and uniq.username == username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username is already taken",
                )

            user = await User.create(session, email, username, get_password_hash(password))
            return UserSchema.model_validate(user)


class AuthenticateUser:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, username: str, password: str) -> UserSchema:
        async with self.async_session() as session:
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
            user = await User.read_by_username(session, username)
            if not user:
                raise credentials_exception
            if not verify_password(password, user.password):
                raise credentials_exception
            return UserSchema.model_validate(user)


class DeleteUser:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, username: str) -> None:
        async with self.async_session.begin() as session:
            await User.delete_user(session, username)
