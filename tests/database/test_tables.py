import pytest
from sqlalchemy import StaticPool, inspect

from auth.models import DBUser  # type: ignore # noqa
from database.session import DatabaseSessionManager
from database.tables import create_tables
from models import Base


@pytest.mark.asyncio
async def test_create_tables() -> None:
    # Set up test database
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    test_manager = DatabaseSessionManager(
        DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    # Teardown
    async with test_manager.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Run the function
    await create_tables(test_manager)

    # Assert that tables exist
    async with test_manager.connect() as conn:

        def check_tables(sync_conn):
            inspector = inspect(sync_conn)
            tables = inspector.get_table_names()
            assert "fct_books" in tables
            assert "dim_authors" in tables
            assert "dim_recommenders" in tables
            assert "users" in tables

        await conn.run_sync(check_tables)
