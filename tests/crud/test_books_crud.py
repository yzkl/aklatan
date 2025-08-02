import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from crud import books
from exceptions.exceptions import EntityDoesNotExistError
from schemas import Book, BookCreate, BookUpdate


async def setup_books_table(session: AsyncSession) -> None:
    test_book = models.Book(
        id=1,
        author_id=1,
        recommender_id=1,
        title="1984",
        year_published=1949,
        is_purchased=True,
        is_read=True,
    )
    session.add(test_book)
    await session.commit()


@pytest.mark.asyncio
async def test_create_improper_book_raises_ValidationError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(ValidationError):
        await books.create_book(
            BookCreate(
                author_id=True, recommender_id=1, title="1984", year_published=1949
            ),
            testing_session,
        )
    with pytest.raises(ValidationError):
        await books.create_book(
            BookCreate(
                author_id=1, recommender_id=False, title="1984", year_published=1949
            ),
            testing_session,
        )
    with pytest.raises(ValidationError):
        await books.create_book(
            BookCreate(author_id=1, recommender_id=1, title=1984, year_published=1949),
            testing_session,
        )
    with pytest.raises(ValidationError):
        await books.create_book(
            BookCreate(
                author_id=1, recommender_id=1, title="1984", year_published="1949"
            ),
            testing_session,
        )
    with pytest.raises(ValidationError):
        await books.create_book(
            BookCreate(
                author_id=1,
                recommender_id=1,
                title="1984",
                year_published=1949,
                is_purchased="True",
            ),
            testing_session,
        )
    with pytest.raises(ValidationError):
        await books.create_book(
            BookCreate(
                author_id=1,
                recommender_id=1,
                title="1984",
                year_published=1949,
                is_read="False",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_create_book_regular(testing_session: AsyncSession) -> None:
    result = await books.create_book(
        BookCreate(author_id=1, recommender_id=1, title="1984", year_published=1949),
        testing_session,
    )

    assert isinstance(result, Book)
    assert result.id == 1  # Should have an id of 1 since it's the first book
    assert result.author_id == 1
    assert result.recommender_id == 1
    assert result.title == "1984"
    assert result.year_published == 1949
    assert not result.is_purchased
    assert not result.is_read

    del result


@pytest.mark.asyncio
async def test_find_nonexistent_book_id_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await books.find_book(9, testing_session)


@pytest.mark.asyncio
async def test_find_book_regular(testing_session: AsyncSession) -> None:
    # Setup
    await setup_books_table(testing_session)

    # Find test book
    result = await books.find_book(1, testing_session)

    assert isinstance(result, models.Book)
    assert result.id == 1
    assert result.author_id == 1
    assert result.recommender_id == 1
    assert result.title == "1984"
    assert result.year_published == 1949
    assert result.is_purchased
    assert result.is_read

    del result


@pytest.mark.asyncio
async def test_find_books_returns_empty_list(testing_session: AsyncSession) -> None:
    # Fetch empty test books table
    result = await books.find_books(testing_session)

    assert isinstance(result, list)
    assert result == []

    del result


@pytest.mark.asyncio
async def test_find_books_regular(testing_session: AsyncSession) -> None:
    # Setup, then add another test book
    await setup_books_table(testing_session)
    await books.create_book(
        BookCreate(
            author_id=1,
            recommender_id=1,
            title="Animal Farm",
            year_published=1945,
            is_purchased=True,
        ),
        testing_session,
    )

    result = await books.find_books(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], models.Book)
    assert isinstance(result[1], models.Book)
    assert result[0].author_id == 1
    assert result[0].recommender_id == 1
    assert result[0].title == "1984"
    assert result[0].year_published == 1949
    assert result[0].is_purchased
    assert result[0].is_read
    assert result[1].author_id == 1
    assert result[1].recommender_id == 1
    assert result[1].title == "Animal Farm"
    assert result[1].year_published == 1945
    assert result[1].is_purchased
    assert not result[1].is_read

    del result


@pytest.mark.asyncio
async def test_read_book(testing_session: AsyncSession) -> None:
    # Setup
    await setup_books_table(testing_session)

    # Find test book
    result = await books.read_book(1, testing_session)

    assert isinstance(result, Book)
    assert result.id == 1
    assert result.author_id == 1
    assert result.recommender_id == 1
    assert result.title == "1984"
    assert result.year_published == 1949
    assert result.is_purchased
    assert result.is_read

    del result


@pytest.mark.asyncio
async def test_read_books(testing_session: AsyncSession) -> None:
    # Setup, then add another test book
    await setup_books_table(testing_session)
    await books.create_book(
        BookCreate(
            author_id=1,
            recommender_id=1,
            title="Animal Farm",
            year_published=1945,
            is_purchased=True,
        ),
        testing_session,
    )

    result = await books.read_books(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Book)
    assert isinstance(result[1], Book)
    assert result[0].author_id == 1
    assert result[0].recommender_id == 1
    assert result[0].title == "1984"
    assert result[0].year_published == 1949
    assert result[0].is_purchased
    assert result[0].is_read
    assert result[1].author_id == 1
    assert result[1].recommender_id == 1
    assert result[1].title == "Animal Farm"
    assert result[1].year_published == 1945
    assert result[1].is_purchased
    assert not result[1].is_read

    del result


@pytest.mark.asyncio
async def test_update_improper_book_raises_ValidationError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(ValidationError):
        await books.update_book(
            id=1, params=BookUpdate(author_id=False), session=testing_session
        )
    with pytest.raises(ValidationError):
        await books.update_book(
            id=1, params=BookUpdate(recommender_id="False"), session=testing_session
        )
    with pytest.raises(ValidationError):
        await books.update_book(
            id=1, params=BookUpdate(title=1984), session=testing_session
        )
    with pytest.raises(ValidationError):
        await books.update_book(
            id=1, params=BookUpdate(year_published="False"), session=testing_session
        )
    with pytest.raises(ValidationError):
        await books.update_book(
            id=1, params=BookUpdate(is_purchased="Soon"), session=testing_session
        )
    with pytest.raises(ValidationError):
        await books.update_book(
            id=1, params=BookUpdate(is_read="False"), session=testing_session
        )


@pytest.mark.asyncio
async def test_update_book_with_improper_foreign_keys_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    # Setup, then update book
    await setup_books_table(testing_session)
    with pytest.raises(EntityDoesNotExistError):
        await books.update_book(
            id=1, params=BookUpdate(author_id=2), session=testing_session
        )
    with pytest.raises(EntityDoesNotExistError):
        await books.update_book(
            id=1, params=BookUpdate(recommender_id=3), session=testing_session
        )


@pytest.mark.asyncio
async def test_update_book_regular(testing_session: AsyncSession) -> None:
    # Setup, then add another test author
    await setup_books_table(testing_session)
    test_author = models.Author(id=2, name="Test Author")
    testing_session.add(test_author)
    await testing_session.commit()

    # Update test book
    result = await books.update_book(
        id=1,
        params=BookUpdate(author_id=2, title="1985", is_read=False),
        session=testing_session,
    )

    assert isinstance(result, Book)
    assert result.id == 1
    assert result.author_id == 2
    assert result.recommender_id == 1
    assert result.title == "1985"
    assert result.year_published == 1949
    assert result.is_purchased
    assert not result.is_read

    del result


@pytest.mark.asyncio
async def test_delete_book(testing_session: AsyncSession) -> None:
    await setup_books_table(testing_session)

    # Delete test book
    result = await books.delete_book(1, testing_session)

    # Check its contents
    assert isinstance(result, Book)
    assert result.id == 1
    assert result.author_id == 1
    assert result.recommender_id == 1
    assert result.title == "1984"
    assert result.year_published == 1949
    assert result.is_purchased
    assert result.is_read

    # Assert that test books table is empty
    with pytest.raises(EntityDoesNotExistError):
        await books.read_book(1, testing_session)
    assert await books.read_books(testing_session) == []

    del result
