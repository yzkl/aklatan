from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import models

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
AsyncTestingSessionLocal = async_sessionmaker(bind=engine_test, expire_on_commit=False)


@pytest_asyncio.fixture
async def testing_session() -> AsyncGenerator[AsyncSession, None]:
    # Setup
    async with engine_test.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    # Populate test tables
    async with AsyncTestingSessionLocal() as session:
        test_author = models.Author(id=1, name="Orwell, George")
        test_recommender = models.Recommender(id=1, name="Peterson, Jordan")
        session.add_all([test_author, test_recommender])
        try:
            await session.commit()
            yield session
        finally:
            # Teardown
            async with engine_test.begin() as conn:
                await conn.run_sync(models.Base.metadata.drop_all)
            await session.close()
