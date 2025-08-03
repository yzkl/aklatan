import pytest
from httpx import AsyncClient

from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError

URL_PREFIX = "/authors/"


@pytest.mark.asyncio
async def test_create_author_returns_http_422_for_missing_name(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_author_returns_http_422_for_invalid_name_type(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"name": False})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_author_raises_EntityAlreadyExists_for_duplicate_author(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityAlreadyExistsError, match="Author already exists"):
        await async_client.post(URL_PREFIX, json={"name": "Orwell, George"})


@pytest.mark.asyncio
async def test_create_author_regular(async_client: AsyncClient) -> None:
    response = await async_client.post(URL_PREFIX, json={"name": "Doe, John"})

    assert response.status_code == 200
    assert response.json()["name"] == "Doe, John"


@pytest.mark.asyncio
async def test_read_author_returns_http_422_for_invalid_input_value(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "true")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_author_raises_EntityDoesNotExistError_for_nonexistent_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await async_client.get(URL_PREFIX + "7")


@pytest.mark.asyncio
async def test_read_author_regular(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "2")

    assert response.status_code == 200
    assert response.json()["name"] == "Dostoevsky, Fyodor"


@pytest.mark.asyncio
async def test_read_authors_returns_empty_list_for_empty_table(
    async_client: AsyncClient,
) -> None:
    # Delete test authors first
    await async_client.delete(URL_PREFIX + "1")
    await async_client.delete(URL_PREFIX + "2")

    # Read authors
    response = await async_client.get(URL_PREFIX)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_update_author_returns_http_422_for_invalid_id_value(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "false", json={"name": "Doe, John"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_author_raises_EntityDoesNotExistError_for_nonexistent_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError, match="does not exist"):
        await async_client.put(URL_PREFIX + "7", json={"name": "Doe, John"})


@pytest.mark.asyncio
async def test_update_author_returns_http_422_for_missing_name(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "1", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_author_returns_http_422_for_invalid_name_type(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "1", json={"name": 7})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_author_raises_EntityAlreadyExistsError_for_duplicate_author(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityAlreadyExistsError, match="already exists"):
        await async_client.put(URL_PREFIX + "2", json={"name": "Orwell, George"})


@pytest.mark.asyncio
async def test_update_author_regular(async_client: AsyncClient) -> None:
    response = await async_client.put(URL_PREFIX + "2", json={"name": "Tolstoy, Leo"})

    assert response.status_code == 200
    assert response.json()["name"] == "Tolstoy, Leo"


@pytest.mark.asyncio
async def test_delete_author_returns_http_422_for_invalid_id_value(
    async_client: AsyncClient,
) -> None:
    response = await async_client.delete(URL_PREFIX + "not-an-id")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_author_raises_EntityDoesNotExistError_for_nonexistent_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError, match="does not exist"):
        await async_client.delete(URL_PREFIX + "5")


@pytest.mark.asyncio
async def test_delete_author_regular(async_client: AsyncClient) -> None:
    response = await async_client.delete(URL_PREFIX + "1")

    assert response.status_code == 200
    assert response.json()["name"] == "Orwell, George"
