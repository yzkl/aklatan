import sqlite3
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from schemas import Recommender, RecommenderCreate, RecommenderUpdate


async def create_recommender(
    params: RecommenderCreate, session: AsyncSession
) -> Recommender:
    db_recommender = models.Recommender(**params.model_dump())
    session.add(db_recommender)
    try:
        await session.commit()
        await session.refresh(db_recommender)
    except (IntegrityError, sqlite3.IntegrityError):
        raise EntityAlreadyExistsError("Recommender already exists.")
    return Recommender.model_validate(db_recommender)


async def find_recommender(id: int, session: AsyncSession) -> models.Recommender:
    db_recommender = await session.get(models.Recommender, id)
    if not db_recommender:
        raise EntityDoesNotExistError(f"Recommender with id {id} does not exist.")
    return db_recommender


async def find_recommenders(session: AsyncSession) -> List[models.Recommender]:
    stmt = select(models.Recommender).order_by(models.Recommender.id)
    db_recommenders = (await session.scalars(stmt)).all()
    return db_recommenders


async def read_recommender(id: int, session: AsyncSession) -> Recommender:
    db_recommender = await find_recommender(id, session)
    return Recommender.model_validate(db_recommender)


async def read_recommenders(session: AsyncSession) -> List[Recommender]:
    db_recommenders = await find_recommenders(session)
    return [
        Recommender.model_validate(db_recommender) for db_recommender in db_recommenders
    ]


async def update_recommender(
    id: int, params: RecommenderUpdate, session: AsyncSession
) -> Recommender:
    db_recommender = await find_recommender(id, session)
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_recommender, attr, value)
    session.add(db_recommender)
    try:
        await session.commit()
        await session.refresh(db_recommender)
    except (IntegrityError, sqlite3.IntegrityError):
        raise EntityAlreadyExistsError("Recommender with this name already exists.")
    return Recommender.model_validate(db_recommender)


async def delete_recommender(id: int, session: AsyncSession) -> Recommender:
    db_recommender = await find_recommender(id, session)
    await session.delete(db_recommender)
    await session.commit()
    return Recommender.model_validate(db_recommender)
