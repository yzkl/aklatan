from typing import List

from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.limiter import limiter
from crud import authors
from database.session import get_db_session
from schemas import Author, AuthorCreate, AuthorUpdate

router = APIRouter(prefix="/authors")


@router.post("/", response_model=Author)
@limiter.limit("10/second")
async def create_author(
    request: Request, params: AuthorCreate, db: AsyncSession = Depends(get_db_session)
) -> Author:
    logger.info(f"Creating author: {params}.")
    result = await authors.create_author(params, db)
    logger.info(f"Created author: {result}.")
    return result


@router.get("/{id}", response_model=Author)
@limiter.limit("10/second")
async def read_author(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Author:
    logger.info(f"Fetching author with id: {id}.")
    result = await authors.read_author(id, db)
    logger.info(f"Fetched author: {result}.")
    return result


@router.get("/", response_model=List[Author])
@limiter.limit("10/second")
async def read_authors(
    request: Request, db: AsyncSession = Depends(get_db_session)
) -> List[Author]:
    logger.info("Fetching authors.")
    result = await authors.read_authors(db)
    logger.info(f"Fetched authors: {result}")
    return result


@router.put("/{id}", response_model=Author)
@limiter.limit("10/second")
async def update_author(
    request: Request,
    id: int,
    params: AuthorUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Author:
    logger.info(f"Updating author with id: {id}.")
    result = await authors.update_author(id, params, db)
    logger.info(f"Updated author: {result}.")
    return result


@router.delete("/{id}", response_model=Author)
@limiter.limit("10/second")
async def delete_author(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Author:
    logger.info(f"Deleting author with id: {id}.")
    result = await authors.delete_author(id, db)
    logger.info(f"Deleted author: {result}.")
    return result
