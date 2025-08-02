import pytest
from httpx import AsyncClient

from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError

URL_PREFIX = "/recommender/"


@pytest.mark.asyncio
async def test_create_recommender_returns_http_422_for_missing_name(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_recommender_returns_http_422_for_invalid_name_type(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"name": False})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_recommender_raises_EntityAlreadyExists_for_duplicate_recommender(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityAlreadyExistsError, match="Recommender already exists"):
        await async_client.post(URL_PREFIX, json={"name": "Peterson, Jordan"})


@pytest.mark.asyncio
async def test_create_recommender_regular(async_client: AsyncClient) -> None:
    response = await async_client.post(URL_PREFIX, json={"name": "Doe, John"})

    assert response.status_code == 200
    assert response.json()["name"] == "Doe, John"


@pytest.mark.asyncio
async def test_read_recommender_returns_http_422_for_invalid_input_value(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "true")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_recommender_raises_EntityDoesNotExistError_for_nonexistent_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await async_client.get(URL_PREFIX + "7")


@pytest.mark.asyncio
async def test_read_recommender_regular(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "2")

    assert response.status_code == 200
    assert response.json()["name"] == "Klavan, Andrew"


@pytest.mark.asyncio
async def test_read_recommenders_returns_empty_list_for_empty_table(
    async_client: AsyncClient,
) -> None:
    # Delete test recommenders first
    await async_client.delete(URL_PREFIX + "1")
    await async_client.delete(URL_PREFIX + "2")

    # Read recommenders
    response = await async_client.get(URL_PREFIX)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_update_recommender_returns_http_422_for_invalid_id_value(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "false", json={"name": "Doe, John"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_recommender_raises_EntityDoesNotExistError_for_nonexistent_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError, match="does not exist"):
        await async_client.put(URL_PREFIX + "7", json={"name": "Doe, John"})


@pytest.mark.asyncio
async def test_update_recommender_returns_http_422_for_missing_name(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "1", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_recommender_returns_http_422_for_invalid_name_type(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "1", json={"name": 7})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_recommender_raises_EntityAlreadyExistsError_for_duplicate_recommender(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityAlreadyExistsError, match="already exists"):
        await async_client.put(URL_PREFIX + "2", json={"name": "Peterson, Jordan"})


@pytest.mark.asyncio
async def test_update_recommender_regular(async_client: AsyncClient) -> None:
    response = await async_client.put(URL_PREFIX + "2", json={"name": "Tolstoy, Leo"})

    assert response.status_code == 200
    assert response.json()["name"] == "Tolstoy, Leo"


@pytest.mark.asyncio
async def test_delete_recommender_returns_http_422_for_invalid_id_value(
    async_client: AsyncClient,
) -> None:
    response = await async_client.delete(URL_PREFIX + "not-an-id")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_recommender_raises_EntityDoesNotExistError_for_nonexistent_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError, match="does not exist"):
        await async_client.delete(URL_PREFIX + "5")


@pytest.mark.asyncio
async def test_delete_recommender_regular(async_client: AsyncClient) -> None:
    response = await async_client.delete(URL_PREFIX + "1")

    assert response.status_code == 200
    assert response.json()["name"] == "Peterson, Jordan"
