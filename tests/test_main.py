from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_read_root(async_client: AsyncClient) -> None:
    response = await async_client.get("/")

    assert response.status_code == 200
    assert "server is running" in response.text


# def test_something() -> None:
#     assert 1 == 1