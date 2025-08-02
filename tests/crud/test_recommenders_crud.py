import pytest
from pydantic import ValidationError
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

import models
from crud import recommenders
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from schemas import Recommender, RecommenderCreate, RecommenderUpdate


@pytest.mark.asyncio
async def test_create_improper_recommender_raises_ValidationError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(ValidationError):
        await recommenders.create_recommender(
            RecommenderCreate(name=False), testing_session
        )
    with pytest.raises(ValidationError):
        await recommenders.create_recommender(
            RecommenderCreate(name=1), testing_session
        )


@pytest.mark.asyncio
async def test_create_recommender_regular(testing_session: AsyncSession) -> None:
    result = await recommenders.create_recommender(
        RecommenderCreate(name="Test Recommender"), testing_session
    )

    assert isinstance(result, Recommender)
    assert (
        result.id == 2
    )  # Should have an id of 2, since a prior test recommender was made upon setup
    assert result.name == "Test Recommender"

    del result


@pytest.mark.asyncio
async def test_find_nonexistent_recommender_id_raises_EntityNotFoundError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await recommenders.find_recommender(7, testing_session)


@pytest.mark.asyncio
async def test_find_recommender_regular(testing_session: AsyncSession) -> None:
    result = await recommenders.find_recommender(1, testing_session)

    assert isinstance(result, models.Recommender)
    assert result.name == "Peterson, Jordan"

    del result


@pytest.mark.asyncio
async def test_find_recommenders_returns_empty_list(
    testing_session: AsyncSession,
) -> None:
    # Delete the test recommender that was set at setup
    await testing_session.execute(delete(models.Recommender))
    await testing_session.commit()

    # Read recommenders
    result = await recommenders.read_recommenders(testing_session)

    assert isinstance(result, list)
    assert result == []

    del result


@pytest.mark.asyncio
async def test_find_recommenders_regular(testing_session: AsyncSession) -> None:
    # Add one more test recommender
    await recommenders.create_recommender(
        RecommenderCreate(id=2, name="Doe, John"), testing_session
    )

    # Read recommenders
    result = await recommenders.find_recommenders(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], models.Recommender)
    assert isinstance(result[1], models.Recommender)
    assert result[0].name == "Peterson, Jordan"
    assert result[1].name == "Doe, John"

    del result


@pytest.mark.asyncio
async def test_read_recommender(testing_session: AsyncSession) -> None:
    result = await recommenders.read_recommender(1, testing_session)

    assert isinstance(result, Recommender)
    assert result.name == "Peterson, Jordan"

    del result


@pytest.mark.asyncio
async def test_read_recommenders(testing_session: AsyncSession) -> None:
    # Add one more test recommender
    await recommenders.create_recommender(
        RecommenderCreate(id=2, name="Doe, John"), testing_session
    )

    # Read recommenders
    result = await recommenders.read_recommenders(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Recommender)
    assert isinstance(result[1], Recommender)
    assert result[0].name == "Peterson, Jordan"
    assert result[1].name == "Doe, John"

    del result


@pytest.mark.asyncio
async def test_update_recommender_raises_EntityAlreadyExistsError(
    testing_session: AsyncSession,
) -> None:
    # Create a second test recommender
    await recommenders.create_recommender(
        RecommenderCreate(id=2, name="Doe, John"), testing_session
    )

    # Update this recommender to have the same name as the original test recommender
    with pytest.raises(EntityAlreadyExistsError):
        await recommenders.update_recommender(
            2, RecommenderUpdate(name="Peterson, Jordan"), testing_session
        )


@pytest.mark.asyncio
async def test_update_recommender_regular(testing_session: AsyncSession) -> None:
    result = await recommenders.update_recommender(
        1, RecommenderUpdate(name="Doe, John"), testing_session
    )

    assert isinstance(result, Recommender)
    assert result.id == 1
    assert result.name == "Doe, John"

    del result


@pytest.mark.asyncio
async def test_delete_recommender(testing_session: AsyncSession) -> None:
    # Delete test recommender
    result = await recommenders.delete_recommender(1, testing_session)

    # Check contents of deleted recommender
    assert isinstance(result, Recommender)
    assert result.id == 1
    assert result.name == "Peterson, Jordan"

    # Check that table is empty
    with pytest.raises(EntityDoesNotExistError):
        await recommenders.read_recommender(1, testing_session)
    assert await recommenders.read_recommenders(testing_session) == []

    del result
