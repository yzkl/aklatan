from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import models
from api.routes import authors, books, recommenders
from database.session import get_db_session

# Set up test app
test_app = FastAPI()
test_app.include_router(authors.router)
test_app.include_router(books.router)
test_app.include_router(recommenders.router)


# Set up test database
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
AsyncTestingSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


# Testing session and override dependency
@pytest_asyncio.fixture
async def testing_session() -> AsyncGenerator[AsyncSession, None]:
    # Setup
    async with test_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    # Populate tables, then yield session
    async with AsyncTestingSessionLocal() as session:
        author1 = models.Author(id=1, name="Orwell, George")
        author2 = models.Author(id=2, name="Dostoevsky, Fyodor")
        recommender1 = models.Recommender(id=1, name="Peterson, Jordan")
        recommender2 = models.Recommender(id=2, name="Klavan, Andrew")
        session.add_all([author1, author2, recommender1, recommender2])
        try:
            await session.commit()
            yield session
        finally:
            # Teardown
            async with test_engine.begin() as conn:
                await conn.run_sync(models.Base.metadata.drop_all)


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
