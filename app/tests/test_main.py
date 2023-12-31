import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(ac: AsyncClient) -> None:
    response = await ac.get(
        "/",
    )
    assert 200 == response.status_code
