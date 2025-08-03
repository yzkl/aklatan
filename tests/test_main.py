from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from auth.models import User
from auth.utils import create_access_token
from database.session import DatabaseSessionManager, get_db_session
from main import app

URL_PREFIX = "api/v1/"


@pytest.mark.asyncio
async def test_read_root_returns_http_200(async_client: AsyncClient) -> None:
    response = await async_client.get("/")

    assert response.status_code == 200
    assert "server is running" in response.text


@pytest.mark.asyncio
async def test_create_author_returns_http_200(async_client: AsyncClient) -> None:
    payload = {"name": "test-author"}
    response = await async_client.post(URL_PREFIX + "authors/", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]


@pytest.mark.asyncio
async def test_read_author_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.get(URL_PREFIX + "authors/1")

    assert response.status_code == 200
    assert response.json()["name"] == testing_data["author1"]


@pytest.mark.asyncio
async def test_read_authors_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.get(URL_PREFIX + "authors/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == testing_data["author1"]
    assert response.json()[1]["name"] == testing_data["author2"]


@pytest.mark.asyncio
async def test_update_author_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {"name": "test-author"}
    response = await async_client.put(URL_PREFIX + "authors/1", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] != testing_data["author1"]
    assert response.json()["name"] == payload["name"]


@pytest.mark.asyncio
async def test_delete_author_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.delete(URL_PREFIX + "authors/2")

    assert response.status_code == 200
    assert response.json()["name"] == testing_data["author2"]


@pytest.mark.asyncio
async def test_create_recommender_returns_http_200(async_client: AsyncClient) -> None:
    payload = {"name": "test-recommender"}
    response = await async_client.post(URL_PREFIX + "authors/", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]


@pytest.mark.asyncio
async def test_read_recommender_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.get(URL_PREFIX + "recommenders/1")

    assert response.status_code == 200
    assert response.json()["name"] == testing_data["recommender1"]


@pytest.mark.asyncio
async def test_read_recommenders_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.get(URL_PREFIX + "recommenders/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == testing_data["recommender1"]
    assert response.json()[1]["name"] == testing_data["recommender2"]


@pytest.mark.asyncio
async def test_update_recommender_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {"name": "test-recommender"}
    response = await async_client.put(URL_PREFIX + "recommenders/1", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] != testing_data["recommender1"]
    assert response.json()["name"] == payload["name"]


@pytest.mark.asyncio
async def test_delete_recommender_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.delete(URL_PREFIX + "recommenders/2")

    assert response.status_code == 200
    assert response.json()["name"] == testing_data["recommender2"]


@pytest.mark.asyncio
async def test_create_book_returns_http_200(async_client: AsyncClient) -> None:
    payload = {
        "author_id": 2,
        "recommender_id": 2,
        "title": "test-title",
        "year_published": 2025,
        "is_purchased": True,
    }
    response = await async_client.post(URL_PREFIX + "books/", json=payload)

    assert response.status_code == 200
    for key in payload:
        assert response.json()[key] == payload[key]
    assert not response.json()["is_read"]


@pytest.mark.asyncio
async def test_read_book_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.get(URL_PREFIX + "books/1")

    assert response.status_code == 200
    for key in testing_data["book1"]:
        assert response.json()[key] == testing_data["book1"][key]


@pytest.mark.asyncio
async def test_read_books_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.get(URL_PREFIX + "books/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    for key in testing_data["book1"]:
        assert response.json()[0][key] == testing_data["book1"][key]
    for key in testing_data["book2"]:
        assert response.json()[1][key] == testing_data["book2"][key]
    assert not response.json()[1]["is_purchased"]
    assert not response.json()[1]["is_read"]


@pytest.mark.asyncio
async def test_update_book_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = testing_data["book1"].copy()
    payload["recommender_id"] = 2
    payload["title"] = "test-title"
    payload["year_published"] = 2025
    payload["is_purchased"] = False
    response = await async_client.put(URL_PREFIX + "books/1", json=payload)

    assert response.status_code == 200
    for key in payload:
        assert response.json()[key] == payload[key]


@pytest.mark.asyncio
async def test_delete_book_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.delete(URL_PREFIX + "books/2")

    assert response.status_code == 200
    for key in testing_data["book2"]:
        assert response.json()[key] == testing_data["book2"][key]


@pytest.mark.asyncio
async def test_register_user_returns_http_200(async_client: AsyncClient) -> None:
    payload = {
        "username": "new-user",
        "email": "new@email.com",
        "password": "weakpassword",
    }
    response = await async_client.post("api/auth/", json=payload)

    assert response.status_code == 200
    assert "Welcome to BuklatAPI, new-user" in response.text


@pytest.mark.asyncio
async def test_login_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {
        "username": testing_data["user"]["username"],
        "password": testing_data["user"]["password"],
    }
    response = await async_client.post(
        "api/auth/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_user_returns_http_401_for_duplicate_username(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = testing_data["user"].copy()
    payload["email"] = "another@email.com"  # Duplicate username, different email
    response = await async_client.post("api/auth/", json=payload)

    assert response.status_code == 401
    assert "Username has already been taken" in response.text


@pytest.mark.asyncio
async def test_register_user_returns_http_401_for_duplicate_email(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = testing_data["user"].copy()
    payload["username"] = "another-user"  # Different username, same email
    response = await async_client.post("api/auth/", json=payload)

    assert response.status_code == 401
    assert "Email has already been taken" in response.text


@pytest.mark.asyncio
async def test_register_user_returns_http_401_for_duplicate_username_and_email(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = testing_data["user"].copy()
    response = await async_client.post("api/auth/", json=payload)

    assert response.status_code == 401
    assert "Username has already been taken" in response.text


@pytest.mark.asyncio
async def test_login_returns_http_401_for_nonexistent_username(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {
        "username": "not-a-username",
        "password": testing_data["user"]["password"],
    }
    response = await async_client.post(
        "api/auth/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert "Invalid username or password" in response.text


@pytest.mark.asyncio
async def test_login_returns_http_401_for_incorrect_password(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {
        "username": testing_data["user"]["username"],
        "password": "wrongpassword",
    }
    response = await async_client.post(
        "api/auth/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert "Invalid username or password" in response.text


@patch("auth.utils.SECRET_KEY", new=SecretStr("test-key"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
@pytest.mark.asyncio
async def test_main_returns_http_401_for_invalid_token(
    testing_session: AsyncSession,
) -> None:
    async def override_db():
        yield testing_session

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        invalid_token = "not-a-token"
        response = await client.get(
            URL_PREFIX + "authors/1",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )

    assert response.status_code == 401
    assert "Invalid" in response.text


@patch("auth.utils.SECRET_KEY", new=SecretStr("test-key"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
@pytest.mark.asyncio
async def test_main_returns_http_401_for_expired_token(
    testing_data: dict,
    testing_session: AsyncSession,
) -> None:
    async def override_db():
        yield testing_session

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        expired_token = create_access_token(
            {"sub": testing_data["user"]},
            now_fn=lambda: datetime(2025, 1, 1),
        )
        response = await client.get(
            URL_PREFIX + "authors/1",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

    assert response.status_code == 401
    assert "expired token" in response.text


@patch("auth.utils.SECRET_KEY", new=SecretStr("test-key"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
@pytest.mark.asyncio
async def test_main_returns_http_401_for_missing_sub_claim(
    testing_session: AsyncSession,
) -> None:
    async def override_db():
        yield testing_session

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        missing_sub = create_access_token({"obj": "no-sub"})
        response = await client.get(
            URL_PREFIX + "authors/1",
            headers={"Authorization": f"Bearer {missing_sub}"},
        )

    assert response.status_code == 401
    assert "Missing 'sub'" in response.text


@patch("auth.utils.SECRET_KEY", new=SecretStr("test-key"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
@pytest.mark.asyncio
async def test_main_returns_http_403_for_deactivated_user(
    testing_data: dict, testing_session: AsyncSession
) -> None:
    async def override_db():
        yield testing_session

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        deactivated_user_token = create_access_token(
            {"sub": testing_data["deactivated_user"]["username"]}
        )
        response = await client.get(
            URL_PREFIX + "authors/1",
            headers={"Authorization": f"Bearer {deactivated_user_token}"},
        )

        assert response.status_code == 403
        assert "Account has been disabled" in response.text


@pytest.mark.asyncio
async def test_read_author_returns_http_404_for_nonexistent_author_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "authors/1000")

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_update_author_returns_http_404_for_nonexistent_author_id(
    async_client: AsyncClient,
) -> None:
    payload = {"name": "new-name"}
    response = await async_client.put(URL_PREFIX + "authors/1000", json=payload)

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_delete_author_returns_http_404_for_nonexistent_author_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "authors/1000")

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_read_recommender_returns_http_404_for_nonexistent_recommender_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "recommenders/1000")

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_update_recommender_returns_http_404_for_nonexistent_recommender_id(
    async_client: AsyncClient,
) -> None:
    payload = {"name": "new-name"}
    response = await async_client.put(URL_PREFIX + "recommenders/1000", json=payload)

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_delete_recommender_returns_http_404_for_nonexistent_recommender_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "recommenders/1000")

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_read_book_returns_http_404_for_nonexistent_book_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "books/1000")

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_update_book_returns_http_404_for_nonexistent_book_id(
    async_client: AsyncClient,
) -> None:
    payload = {"title": "new-name"}
    response = await async_client.put(URL_PREFIX + "books/1000", json=payload)

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_update_book_returns_http_404_for_nonexistent_author_id(
    async_client: AsyncClient,
) -> None:
    payload = {"author_id": 1000}
    response = await async_client.put(URL_PREFIX + "books/1", json=payload)

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_update_book_returns_http_404_for_nonexistent_recommender_id(
    async_client: AsyncClient,
) -> None:
    payload = {"recommender_id": 1000}
    response = await async_client.put(URL_PREFIX + "books/1", json=payload)

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_delete_book_returns_http_404_for_nonexistent_book_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "authors/1000")

    assert response.status_code == 404
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_create_author_returns_http_409_for_duplicate_author(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {"name": testing_data["author1"]}
    response = await async_client.post(URL_PREFIX + "authors/", json=payload)

    assert response.status_code == 409
    assert "already exists" in response.text


@pytest.mark.asyncio
async def test_update_author_returns_http_409_for_duplicate_author(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {"name": testing_data["author1"]}
    response = await async_client.put(URL_PREFIX + "authors/2", json=payload)

    assert response.status_code == 409
    assert "already exists" in response.text


@pytest.mark.asyncio
async def test_create_recommender_returns_http_409_for_duplicate_recommender(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {"name": testing_data["recommender1"]}
    response = await async_client.post(URL_PREFIX + "recommenders/", json=payload)

    assert response.status_code == 409
    assert "already exists" in response.text


@pytest.mark.asyncio
async def test_update_recommender_returns_http_409_for_duplicate_recommender(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = {"name": testing_data["recommender1"]}
    response = await async_client.put(URL_PREFIX + "recommenders/2", json=payload)

    assert response.status_code == 409
    assert "already exists" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_500_for_internal_server_error(testing_data) -> None:
    async def override_db():
        DATABASE_URL = "sqlite+aiosqlite:///:memory:"
        sessionmanager = DatabaseSessionManager(
            DATABASE_URL, connect_args={"check_same_thread": False}
        )
        sessionmanager.engine = None  # Induce an internal server error
        async with sessionmanager.session() as session:
            yield session

    async def override_user():
        yield User(
            username=testing_data["user"]["username"],
            email=testing_data["user"]["email"],
            is_active=True,
        )

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_active_user] = override_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(URL_PREFIX + "authors/1")

        assert response.status_code == 500
        assert "Service is unavailable." in response.text
