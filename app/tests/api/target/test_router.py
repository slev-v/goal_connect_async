import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.user.jwt import create_access_token
from app.api.user.security import get_password_hash
from app.tests.utils import ID_STRING


async def setup_data(session: AsyncSession) -> None:
    from app.models import Goal, Target, User

    user1 = User(email="test1@gmail.com", username="test1", password=get_password_hash("Testtest1"))
    session.add_all([user1])
    await session.flush()

    goal1 = Goal(title="test1", description="test1", private=True, user_id=user1.id)
    session.add_all([goal1])
    await session.flush()

    target1 = Target(title="test1", target=7, goal_id=goal1.id)
    target2 = Target(title="test2", target=3, goal_id=goal1.id)
    session.add_all([target1, target2])
    await session.flush()

    await session.commit()


@pytest.mark.asyncio
async def test_target_add(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import Goal, User

    await setup_data(session)

    user = await User.read_by_username(session, "test1")
    assert user
    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    goal = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=1, offset=0)][0]
    target_count = len(goal.targets)

    response = await ac.post(
        f"/target?goal_id={goal.id}",
        cookies=cookies,
        json={"title": "test_add", "target": 444, "progress": 77},
    )

    assert response.status_code == 201
    print(response.content)
    expected = {"title": "test_add", "target": 444, "progress": 77, "id": ID_STRING}
    assert expected == response.json()

    await session.refresh(goal)
    assert target_count + 1 == len(goal.targets)


@pytest.mark.asyncio
async def test_target_delete(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import Goal, User

    await setup_data(session)

    user = await User.read_by_username(session, "test1")
    assert user
    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    goal = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=1, offset=0)][0]
    targets_count = len(goal.targets)
    target = goal.targets[0]

    response = await ac.delete(
        f"target/{target.id}?goal_id={goal.id}",
        cookies=cookies,
    )
    assert 204 == response.status_code

    await session.refresh(goal)
    assert targets_count - 1 == len(goal.targets)


@pytest.mark.asyncio
async def test_target_update(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import Goal, User

    await setup_data(session)

    user = await User.read_by_username(session, "test1")
    assert user
    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    goal = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=1, offset=0)][0]
    target = goal.targets[0]
    assert target.title == "test1"
    assert target.target == 7
    assert target.progress == 0

    response = await ac.put(
        f"target/{target.id}?goal_id={goal.id}",
        cookies=cookies,
        json={"title": "test_update", "target": 222, "progress": 222},
    )
    assert 200 == response.status_code

    print(response.content)
    expected = {"title": "test_update", "target": 222, "progress": 222, "id": target.id}
    assert expected == response.json()

    await session.refresh(target)
    assert target.title == "test_update"
    assert target.target == 222
    assert target.progress == 222
