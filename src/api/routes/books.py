from typing import List

from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.limiter import limiter
from crud import books
from database.session import get_db_session
from schemas import Book, BookCreate, BookUpdate

router = APIRouter(prefix="/book")


@router.post("/", response_model=Book)
@limiter.limit("10/second")
async def create_book(
    request: Request, params: BookCreate, db: AsyncSession = Depends(get_db_session)
) -> Book:
    logger.info(f"Creating book: {params}.")
    result = await books.create_book(params, db)
    logger.info(f"Created book: {result}.")
    return result


@router.get("/{id}", response_model=Book)
@limiter.limit("10/second")
async def read_book(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Book:
    logger.info(f"Fetching book with id: {id}.")
    result = await books.read_book(id, db)
    logger.info(f"Fetched book: {result}.")
    return result


@router.get("/", response_model=List[Book])
@limiter.limit("10/second")
async def read_books(
    request: Request, db: AsyncSession = Depends(get_db_session)
) -> List[Book]:
    logger.info("Fetching books.")
    result = await books.read_books(db)
    logger.info(f"Fetched books: {result}")
    return result


@router.put("/{id}", response_model=Book)
@limiter.limit("10/second")
async def update_book(
    request: Request,
    id: int,
    params: BookUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Book:
    logger.info(f"Updating book with id: {id}.")
    result = await books.update_book(id, params, db)
    logger.info(f"Updated book: {result}.")
    return result


@router.delete("/{id}", response_model=Book)
@limiter.limit("10/second")
async def delete_book(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Book:
    logger.info(f"Deleting book with id: {id}.")
    result = await books.delete_book(id, db)
    logger.info(f"Deleted book: {result}.")
    return result
