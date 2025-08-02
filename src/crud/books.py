from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from exceptions.exceptions import EntityDoesNotExistError
from schemas import Book, BookCreate, BookUpdate


async def create_book(params: BookCreate, session: AsyncSession) -> Book:
    db_book = models.Book(**params.model_dump())
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return Book.model_validate(db_book)


async def find_book(id: int, session: AsyncSession) -> models.Book:
    db_book = await session.get(models.Book, id)
    if not db_book:
        raise EntityDoesNotExistError(f"Book with id {id} does not exist.")
    return db_book


async def find_books(session: AsyncSession) -> List[models.Book]:
    stmt = select(models.Book).order_by(models.Book.id)
    db_books = (await session.scalars(stmt)).all()
    return db_books


async def read_book(id: int, session: AsyncSession) -> Book:
    db_book = await find_book(id, session)
    return Book.model_validate(db_book)


async def read_books(session: AsyncSession) -> List[Book]:
    db_books = await find_books(session)
    return [Book.model_validate(db_book) for db_book in db_books]


async def update_book(id: int, params: BookUpdate, session: AsyncSession) -> Book:
    db_book = await find_book(id, session)

    update_data = params.model_dump(exclude_unset=True)

    # Validate author id if provided
    if "author_id" in update_data:
        author = await session.get(models.Author, update_data["author_id"])
        if not author:
            raise EntityDoesNotExistError(
                f"Author with id {update_data['author_id']} does not exist."
            )

    # Validate recommender id if provided
    if "recommender_id" in update_data:
        recommender = await session.get(
            models.Recommender, update_data["recommender_id"]
        )
        if not recommender:
            raise EntityDoesNotExistError(
                f"Recommender with id {update_data['recommender_id']} does not exist."
            )

    for attr, value in update_data.items():
        setattr(db_book, attr, value)
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return Book.model_validate(db_book)


async def delete_book(id: int, session: AsyncSession) -> Book:
    db_book = await find_book(id, session)
    await session.delete(db_book)
    await session.commit()
    return Book.model_validate(db_book)
