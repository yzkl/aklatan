from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import models
from auth.dependencies import get_current_active_user
from auth.models import DBUser, User
from auth.utils import get_password_hash
from database.session import get_db_session
from main import app

TEST_DATA = {
    "author1": "Orwell, George",
    "author2": "Austen, Jane",
    "recommender1": "Prager, Dennis",
    "recommender2": "Klavan, Andrew",
    "book1": {
        "author_id": 1,
        "recommender_id": 1,
        "title": "1984",
        "year_published": 1949,
        "is_purchased": True,
        "is_read": True,
    },
    "book2": {
        "author_id": 1,
        "recommender_id": 1,
        "title": "Animal Farm",
        "year_published": 1945,
    },
    "user": {
        "username": "test-user",
        "email": "email@email.com",
        "password": "strongpassword",
    },
    "deactivated_user": {
        "username": "x-user",
        "email": "x@email.com",
        "password": "xpassword",
        "is_active": False,
    },
    "secret_key": SecretStr("test-key"),
    "algorithm": SecretStr("HS256"),
}


@pytest.fixture
def testing_data() -> dict:
    return TEST_DATA.copy()


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
AsyncTestingSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def testing_session(testing_data) -> AsyncGenerator[AsyncSession, None]:
    # Setup
    async with test_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    # Populate tablesm then yield session
    async with AsyncTestingSessionLocal() as session:
        author1 = models.Author(id=1, name=testing_data["author1"])
        author2 = models.Author(id=2, name=testing_data["author2"])
        recommender1 = models.Recommender(id=1, name=testing_data["recommender1"])
        recommender2 = models.Recommender(id=2, name=testing_data["recommender2"])
        book1 = models.Book(id=1, **testing_data["book1"])
        book2 = models.Book(id=2, **testing_data["book2"])
        user1 = DBUser(
            username=testing_data["user"]["username"],
            email=testing_data["user"]["email"],
            hashed_password=get_password_hash(
                SecretStr(testing_data["user"]["password"])
            ),
        )
        user2 = DBUser(
            username=testing_data["deactivated_user"]["username"],
            email=testing_data["deactivated_user"]["email"],
            hashed_password=get_password_hash(
                SecretStr(testing_data["deactivated_user"]["password"])
            ),
            is_active=testing_data["deactivated_user"]["is_active"],
        )
        session.add_all(
            [author1, author2, recommender1, recommender2, book1, book2, user1, user2]
        )
        try:
            await session.commit()
            yield session
        finally:
            # Teardown
            async with test_engine.begin() as conn:
                await conn.run_sync(models.Base.metadata.drop_all)


@pytest_asyncio.fixture
async def override_get_current_active_user(testing_data) -> AsyncGenerator[User, None]:
    yield User(
        username=testing_data["user"]["username"],
        email=testing_data["user"]["email"],
        is_active=True,
    )


@pytest_asyncio.fixture
async def async_client(
    testing_session, override_get_current_active_user
) -> AsyncGenerator[AsyncClient, None]:
    async def override_db():
        yield testing_session

    async def override_user():
        yield override_get_current_active_user

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_active_user] = override_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        try:
            yield client
        finally:
            app.dependency_overrides = {}

