import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.user.jwt import create_access_token
from app.api.user.security import get_password_hash
from app.tests.utils import ID_STRING


async def setup_data(session: AsyncSession) -> None:
    from app.models import Goal, Target, User

    user1 = User(email="test1@gmail.com", username="test1", password=get_password_hash("Testtest1"))
    user2 = User(email="test2@gmail.com", username="test2", password=get_password_hash("Testtest1"))
    session.add_all([user1, user2])
    await session.flush()

    goal1 = Goal(title="test1", description="test1", private=True, user_id=user1.id)
    goal2 = Goal(title="test2", description="test2", private=False, user_id=user1.id)
    goal3 = Goal(title="test3", description="test3", private=False, user_id=user2.id)
    session.add_all([goal1, goal2, goal3])
    await session.flush()

    target1 = Target(title="test1", target=7, goal_id=goal1.id)
    target2 = Target(title="test2", target=3, goal_id=goal2.id)
    target3 = Target(title="test3", target=3, goal_id=goal1.id)
    target4 = Target(title="test4", target=666, progress=22, goal_id=goal3.id)
    session.add_all([target1, target2, target3, target4])
    await session.flush()

    await session.commit()


@pytest.mark.asyncio
async def test_goal_add(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import Goal, User

    await setup_data(session)

    user = await User.read_by_username(session, "test2")
    assert user
    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test2'})}"}
    goals = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=100, offset=0)]
    goals_count = len(goals)

    response = await ac.post(
        "/goal",
        cookies=cookies,
        json={
            "title": "test4",
            "description": "test4",
            "private": True,
            "user_id": user.id,
            "targets": [{"title": "target_test4", "target": 5, "progress": 2}],
        },
    )

    print(response.content)
    assert 201 == response.status_code
    expected = {
        "title": "test4",
        "description": "test4",
        "private": True,
        "id": ID_STRING,
        "user_id": user.id,
        "targets": [{"title": "target_test4", "target": 5, "progress": 2, "id": ID_STRING}],
    }
    assert expected == response.json()

    goals = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=100, offset=0)]
    assert len(goals) == goals_count + 1


@pytest.mark.asyncio
async def test_all_goal_read(ac: AsyncClient, session: AsyncSession) -> None:
    await setup_data(session)

    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    response = await ac.get("/goal", cookies=cookies)

    print(response.content)
    assert 200 == response.status_code
    expected = {
        "goals": [
            {
                "title": "test1",
                "description": "test1",
                "private": True,
                "id": ID_STRING,
                "user_id": ID_STRING,
                "targets": [
                    {"title": "test1", "target": 7, "progress": 0, "id": ID_STRING},
                    {"title": "test3", "target": 3, "progress": 0, "id": ID_STRING},
                ],
            },
            {
                "title": "test2",
                "description": "test2",
                "private": False,
                "id": ID_STRING,
                "user_id": ID_STRING,
                "targets": [{"title": "test2", "target": 3, "progress": 0, "id": ID_STRING}],
            },
        ]
    }
    assert expected == response.json()


@pytest.mark.asyncio
async def test_goal_public_read(ac: AsyncClient, session: AsyncSession) -> None:
    await setup_data(session)

    response = await ac.get("/goal/public")

    print(response.content)
    expected = {
        "goals": [
            {
                "title": "test2",
                "description": "test2",
                "private": False,
                "id": ID_STRING,
                "user_id": ID_STRING,
                "targets": [{"title": "test2", "target": 3, "progress": 0, "id": ID_STRING}],
            },
            {
                "title": "test3",
                "description": "test3",
                "private": False,
                "id": ID_STRING,
                "user_id": ID_STRING,
                "targets": [{"title": "test4", "target": 666, "progress": 22, "id": ID_STRING}],
            },
        ]
    }
    assert expected == response.json()


@pytest.mark.asyncio
async def test_read_goal_by_id(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import Goal, User

    await setup_data(session)

    user = await User.read_by_username(session, "test1")
    assert user
    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    goal = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=1, offset=0)][0]

    response = await ac.get(f"/goal/{goal.id}", cookies=cookies)

    print(response.content)
    assert 200 == response.status_code
    expected = {
        "title": "test1",
        "description": "test1",
        "private": True,
        "id": goal.id,
        "user_id": user.id,
        "targets": [
            {"title": "test1", "target": 7, "progress": 0, "id": ID_STRING},
            {"title": "test3", "target": 3, "progress": 0, "id": ID_STRING},
        ],
    }
    assert expected == response.json()


@pytest.mark.asyncio
async def test_goal_delete(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import Goal, User

    await setup_data(session)

    user = await User.read_by_username(session, "test1")
    assert user
    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    goals = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=100, offset=0)]
    goals_count = len(goals)

    response = await ac.delete(f"/goal/{goals[0].id}", cookies=cookies)

    print(response.content)
    assert 204 == response.status_code

    goals = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=100, offset=0)]
    assert len(goals) == goals_count - 1


@pytest.mark.asyncio
async def test_goal_update(ac: AsyncClient, session: AsyncSession) -> None:
    from app.models import Goal, User

    await setup_data(session)

    user = await User.read_by_username(session, "test1")
    assert user
    cookies = {"access_token": f"Bearer {create_access_token(data={'sub': 'test1'})}"}
    goal = [gl async for gl in Goal.read_user_goals(session, user_id=user.id, limit=1, offset=0)][0]
    old_goal_id = goal.id

    response = await ac.put(
        f"/goal/{goal.id}",
        cookies=cookies,
        json={"title": "updated", "description": "updated", "private": False},
    )

    assert 200 == response.status_code
    print(response.content)
    expected = {
        "title": "updated",
        "description": "updated",
        "private": False,
        "id": goal.id,
        "user_id": user.id,
        "targets": [
            {"title": "test1", "target": 7, "progress": 0, "id": ID_STRING},
            {"title": "test3", "target": 3, "progress": 0, "id": ID_STRING},
        ],
    }
    assert expected == response.json()

    await session.refresh(goal)
    assert old_goal_id == goal.id
    assert goal.title == "updated"
    assert goal.private is False
    assert goal.description == "updated"
