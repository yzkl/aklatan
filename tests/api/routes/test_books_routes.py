import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exceptions import EntityDoesNotExistError
from models import Book

URL_PREFIX = "/book/"

TEST_PAYLOAD = {
    "author_id": 1,
    "recommender_id": 2,
    "title": "test-book",
    "year_published": 2025,
}
TEST_BOOK_1 = {
    "author_id": 1,
    "recommender_id": 1,
    "title": "1984",
    "year_published": 1949,
    "is_purchased": True,
    "is_read": True,
}
TEST_BOOK_2 = {
    "author_id": 1,
    "recommender_id": 1,
    "title": "Animal Farm",
    "year_published": 1945,
}


async def setup_books_table(session: AsyncSession):
    test_book_1 = Book(id=1, **TEST_BOOK_1)
    test_book_2 = Book(id=2, **TEST_BOOK_2)
    session.add_all([test_book_1, test_book_2])
    await session.commit()


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_missing_author_id_input(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload.pop("author_id")
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_missing_recommender_id_input(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload.pop("recommender_id")
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_missing_title_input(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload.pop("title")
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_missing_year_published_input(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload.pop("year_published")
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_improper_author_id_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["author_id"] = True
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_improper_recommender_id_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["recommender_id"] = "False"
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_improper_title_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["title"] = 1234
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_improper_year_published_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["year_published"] = "last year"
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_improper_is_purchased_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["is_purchased"] = "true"
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_returns_http_422_for_improper_is_read_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["is_read"] = 422
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_book_regular(async_client: AsyncClient) -> None:
    response = await async_client.post(URL_PREFIX, json=TEST_PAYLOAD)

    assert response.status_code == 200
    for key in TEST_PAYLOAD:
        assert response.json()[key] == TEST_PAYLOAD[key]


@pytest.mark.asyncio
async def test_create_book_with_is_purchased_true(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["is_purchased"] = True
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 200
    for key in payload:
        assert response.json()[key] == payload[key]


@pytest.mark.asyncio
async def test_create_book_with_is_read_true(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["is_read"] = True
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 200
    for key in payload:
        assert response.json()[key] == payload[key]


@pytest.mark.asyncio
async def test_create_book_with_both_is_purchased_and_is_read_true(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["is_purchased"] = True
    payload["is_read"] = True
    response = await async_client.post(URL_PREFIX, json=payload)

    assert response.status_code == 200
    for key in payload:
        assert response.json()[key] == payload[key]


@pytest.mark.asyncio
async def test_read_book_returns_http_422_for_improper_book_id_input(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "true")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_book_raises_EntityDoesNotExistError_for_nonexistent_book_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await async_client.get(URL_PREFIX + "100")


@pytest.mark.asyncio
async def test_read_book_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_books_table(testing_session)

    response = await async_client.get(URL_PREFIX + "1")

    assert response.status_code == 200
    for key in TEST_BOOK_1:
        assert response.json()[key] == TEST_BOOK_1[key]


@pytest.mark.asyncio
async def test_read_books_returns_empty_list(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_read_books_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_books_table(testing_session)

    response = await async_client.get(URL_PREFIX)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for key in TEST_BOOK_1:
        assert response.json()[0][key] == TEST_BOOK_1[key]
    for key in TEST_BOOK_2:
        assert response.json()[1][key] == TEST_BOOK_2[key]


@pytest.mark.asyncio
async def test_update_book_returns_http_422_for_improper_book_id_type(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "not-an-id", json=TEST_PAYLOAD)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_returns_http_422_for_improper_author_id_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["author_id"] = "1"
    response = await async_client.put(URL_PREFIX + "1", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_returns_http_422_for_improper_recommender_id_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["recommender_id"] = False
    response = await async_client.put(URL_PREFIX + "1", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_returns_http_422_for_improper_title_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["title"] = False
    response = await async_client.put(URL_PREFIX + "1", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_returns_http_422_for_improper_year_published_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["year_published"] = "2025"
    response = await async_client.put(URL_PREFIX + "1", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_returns_http_422_for_improper_is_purchased_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["is_purchased"] = 422
    response = await async_client.put(URL_PREFIX + "1", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_returns_http_422_for_improper_is_read_type(
    async_client: AsyncClient,
) -> None:
    payload = TEST_PAYLOAD.copy()
    payload["is_read"] = "True"
    response = await async_client.put(URL_PREFIX + "1", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_raises_EntityDoesNotExistError_for_nonexistent_book_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await async_client.put(URL_PREFIX + "1", json=TEST_PAYLOAD)


@pytest.mark.asyncio
async def test_update_book_raises_EntityDoesNotExistError_for_nonexistent_author_id(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_books_table(testing_session)
    with pytest.raises(EntityDoesNotExistError):
        await async_client.put(URL_PREFIX + "1", json={"author_id": 1000})


@pytest.mark.asyncio
async def test_update_book_raises_EntityDoesNotExistError_for_nonexistent_recommender_id(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_books_table(testing_session)
    with pytest.raises(EntityDoesNotExistError):
        await async_client.put(URL_PREFIX + "1", json={"recommender_id": 1000})


@pytest.mark.asyncio
async def test_update_book_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_books_table(testing_session)
    payload = TEST_BOOK_2.copy()
    payload["recommender_id"] = 2
    payload["title"] = "test-title"
    payload["is_read"] = True

    response = await async_client.put(URL_PREFIX + "2", json=payload)

    assert response.status_code == 200
    for key in payload:
        assert response.json()[key] == payload[key]


@pytest.mark.asyncio
async def test_delete_book_returns_http_422_for_improper_book_id_value(
    async_client: AsyncClient,
) -> None:
    response = await async_client.delete(URL_PREFIX + "not-an-id")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_book_raises_EntityDoesNotExistError_for_nonexistent_book_id(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await async_client.delete(URL_PREFIX + "404")


@pytest.mark.asyncio
async def test_delete_book_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_books_table(testing_session)

    response = await async_client.delete(URL_PREFIX + "2")

    assert response.status_code == 200
    for key in TEST_BOOK_2:
        assert response.json()[key] == TEST_BOOK_2[key]
