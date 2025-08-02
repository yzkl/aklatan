import sqlite3
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from schemas import Author, AuthorCreate, AuthorUpdate


async def create_author(params: AuthorCreate, session: AsyncSession) -> Author:
    db_author = models.Author(**params.model_dump())
    session.add(db_author)
    try:
        await session.commit()
        await session.refresh(db_author)
    except (IntegrityError, sqlite3.IntegrityError):
        raise EntityAlreadyExistsError("Author already exists.")
    return Author.model_validate(db_author)


async def find_author(id: int, session: AsyncSession) -> models.Author:
    db_author = await session.get(models.Author, id)
    if not db_author:
        raise EntityDoesNotExistError(f"Author with id {id} does not exist.")
    return db_author


async def find_authors(session: AsyncSession) -> List[models.Author]:
    stmt = select(models.Author).order_by(models.Author.id)
    db_authors = (await session.scalars(stmt)).all()
    return db_authors


async def read_author(id: int, session: AsyncSession) -> Author:
    db_author = await find_author(id, session)
    return Author.model_validate(db_author)


async def read_authors(session: AsyncSession) -> List[Author]:
    db_authors = await find_authors(session)
    return [Author.model_validate(db_author) for db_author in db_authors]


async def update_author(id: int, params: AuthorUpdate, session: AsyncSession) -> Author:
    db_author = await find_author(id, session)
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_author, attr, value)
    session.add(db_author)
    try:
        await session.commit()
        await session.refresh(db_author)
    except (IntegrityError, sqlite3.IntegrityError):
        raise EntityAlreadyExistsError("Author with this name already exists.")
    return Author.model_validate(db_author)


async def delete_author(id: int, session: AsyncSession) -> Author:
    db_author = await find_author(id, session)
    await session.delete(db_author)
    await session.commit()
    return Author.model_validate(db_author)
