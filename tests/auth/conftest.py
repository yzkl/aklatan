from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth.models import DBUser
from auth.routes import auth_router
from auth.utils import get_password_hash
from database.session import get_db_session
from models import Base

# Set up test objects
TEST_DATA = {
    "username": "test-user",
    "email": "email@email.com",
    "password": SecretStr("strongpassword"),
    "secret_key": SecretStr("strongkey"),
    "algorithm": SecretStr("HS256"),
    "register_payload": {
        "username": "some-user",
        "email": "some@email.com",
        "password": "some-pass",
    },
}
TEST_DATA["token_payload"] = {"sub": TEST_DATA["username"]}


@pytest.fixture
def testing_data() -> dict:
    return TEST_DATA.copy()


# Set up test app
test_app = FastAPI()
test_app.include_router(auth_router)


# Set up test database
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
AsyncTestingSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


# Override dependencies and create test client
@pytest_asyncio.fixture
async def testing_session(testing_data) -> AsyncGenerator[AsyncSession, None]:
    # Setup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Populate tables, then yield session
    async with AsyncTestingSessionLocal() as session:
        db_user = DBUser(
            username=testing_data["username"],
            email=testing_data["email"],
            hashed_password=get_password_hash(testing_data["password"]),
        )
        session.add(db_user)
        try:
            await session.commit()
            yield session
        finally:
            # Teardown
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client(testing_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session():
        yield testing_session

    test_app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        try:
            yield client
        finally:
            test_app.dependency_overrides = {}
