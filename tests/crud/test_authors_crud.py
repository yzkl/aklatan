import pytest
from pydantic import ValidationError
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

import models
from crud import authors
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from schemas import Author, AuthorCreate, AuthorUpdate


@pytest.mark.asyncio
async def test_create_improper_author_raises_ValidationError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(ValidationError):
        await authors.create_author(AuthorCreate(name=False), testing_session)
    with pytest.raises(ValidationError):
        await authors.create_author(AuthorCreate(name=1), testing_session)


@pytest.mark.asyncio
async def test_create_author_regular(testing_session: AsyncSession) -> None:
    result = await authors.create_author(
        AuthorCreate(name="Test Author"), testing_session
    )

    assert isinstance(result, Author)
    assert (
        result.id == 2
    )  # Should have an id of 2, since a prior test author was made upon setup
    assert result.name == "Test Author"

    del result


@pytest.mark.asyncio
async def test_find_nonexistent_author_id_raises_EntityNotFoundError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await authors.find_author(7, testing_session)


@pytest.mark.asyncio
async def test_find_author_regular(testing_session: AsyncSession) -> None:
    result = await authors.find_author(1, testing_session)

    assert isinstance(result, models.Author)
    assert result.name == "Orwell, George"

    del result


@pytest.mark.asyncio
async def test_find_authors_returns_empty_list(testing_session: AsyncSession) -> None:
    # Delete the test author that was set at setup
    await testing_session.execute(delete(models.Author))
    await testing_session.commit()

    # Read authors
    result = await authors.read_authors(testing_session)

    assert isinstance(result, list)
    assert result == []

    del result


@pytest.mark.asyncio
async def test_find_authors_regular(testing_session: AsyncSession) -> None:
    # Add one more test author
    await authors.create_author(AuthorCreate(id=2, name="Doe, John"), testing_session)

    # Read authors
    result = await authors.find_authors(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], models.Author)
    assert isinstance(result[1], models.Author)
    assert result[0].name == "Orwell, George"
    assert result[1].name == "Doe, John"

    del result


@pytest.mark.asyncio
async def test_read_author(testing_session: AsyncSession) -> None:
    result = await authors.read_author(1, testing_session)

    assert isinstance(result, Author)
    assert result.name == "Orwell, George"

    del result


@pytest.mark.asyncio
async def test_read_authors(testing_session: AsyncSession) -> None:
    # Add one more test author
    await authors.create_author(AuthorCreate(id=2, name="Doe, John"), testing_session)

    # Read authors
    result = await authors.read_authors(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Author)
    assert isinstance(result[1], Author)
    assert result[0].name == "Orwell, George"
    assert result[1].name == "Doe, John"

    del result


@pytest.mark.asyncio
async def test_update_author_raises_EntityAlreadyExistsError(
    testing_session: AsyncSession,
) -> None:
    # Create a second test author
    await authors.create_author(AuthorCreate(id=2, name="Doe, John"), testing_session)

    # Update this author to have the same name as the original test author
    with pytest.raises(EntityAlreadyExistsError):
        await authors.update_author(
            2, AuthorUpdate(name="Orwell, George"), testing_session
        )


@pytest.mark.asyncio
async def test_update_author_regular(testing_session: AsyncSession) -> None:
    result = await authors.update_author(
        1, AuthorUpdate(name="Doe, John"), testing_session
    )

    assert isinstance(result, Author)
    assert result.id == 1
    assert result.name == "Doe, John"

    del result


@pytest.mark.asyncio
async def test_delete_author(testing_session: AsyncSession) -> None:
    # Delete test author
    result = await authors.delete_author(1, testing_session)

    # Check contents of deleted author
    assert isinstance(result, Author)
    assert result.id == 1
    assert result.name == "Orwell, George"

    # Check that table is empty
    with pytest.raises(EntityDoesNotExistError):
        await authors.read_author(1, testing_session)
    assert await authors.read_authors(testing_session) == []

    del result
