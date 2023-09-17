from datetime import datetime

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.user.jwt import create_access_token
from app.api.user.security import get_password_hash
from app.config import settings
from app.tests.utils import ID_STRING


async def setup_data(session: AsyncSession) -> None:
    from app.models import User

    user1 = User(email="test1@gmail.com", username="test1", password=get_password_hash("Testtest1"))
    user2 = User(email="test2@gmail.com", username="test2", password=get_password_hash("Testtest1"))
    session.add_all([user1, user2])

    await session.flush()
    await session.commit()


@pytest.mark.asyncio
async def test_user_create(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import User

    response = await ac.post(
        "/user", json={"email": "test3@gmail.com", "username": "test3", "password": "Testtest1"}
    )

    print(response.content)
    assert 201 == response.status_code
    expected = {"id": ID_STRING, "email": "test3@gmail.com", "username": "test3"}
    assert expected == response.json()

    user = await User.read_by_id(session, response.json()["id"])
    assert user
    assert user.email == "test3@gmail.com"
    assert user.username == "test3"


@pytest.mark.asyncio
async def test_user_read(ac: AsyncClient, session: AsyncSession) -> None:
    await setup_data(session)

    response = await ac.get("user/test1")

    print(response.content)

    assert 200 == response.status_code
    expected = {"id": ID_STRING, "email": "test1@gmail.com", "username": "test1"}
    assert expected == response.json()


@pytest.mark.asyncio
async def test_user_auth(ac: AsyncClient, session: AsyncSession) -> None:
    await setup_data(session)

    response = await ac.post("/user/token", data={"username": "test1", "password": "Testtest1"})

    print(response.content)

    decoded = jwt.decode(
        response.json()["access_token"], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    token_exp = datetime.fromtimestamp(decoded["exp"])
    cookie_response = response.cookies["access_token"][1:-1]
    assert 200 == response.status_code
    assert decoded["sub"] == "test1"
    assert token_exp > datetime.utcnow()
    assert cookie_response == f"Bearer {response.json()['access_token']}"


@pytest.mark.asyncio
async def test_user_current(ac: AsyncClient, session: AsyncSession) -> None:
    await setup_data(session)

    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    response = await ac.get("/user", cookies=cookies)

    print(response.content)

    expected = {"id": ID_STRING, "email": "test1@gmail.com", "username": "test1"}
    assert response.json() == expected


@pytest.mark.asyncio
async def test_user_delete(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import User

    await setup_data(session)

    assert await User.read_by_username(session, "test1")

    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    response = await ac.delete("/user", cookies=cookies)

    print(response.content)

    assert 204 == response.status_code
    assert await User.read_by_username(session, "test1") is None


@pytest.mark.asyncio
async def test_user_logout(ac: AsyncClient, session: AsyncSession) -> None:
    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    response = await ac.delete("/user/token", cookies=cookies)

    assert response.status_code == 204
