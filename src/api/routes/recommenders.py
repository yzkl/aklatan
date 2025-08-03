from typing import List

from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.limiter import limiter
from crud import recommenders
from database.session import get_db_session
from schemas import Recommender, RecommenderCreate, RecommenderUpdate

router = APIRouter(prefix="/recommenders")


@router.post("/", response_model=Recommender)
@limiter.limit("10/second")
async def create_recommender(
    request: Request,
    params: RecommenderCreate,
    db: AsyncSession = Depends(get_db_session),
) -> Recommender:
    logger.info(f"Creating recommender: {params}.")
    result = await recommenders.create_recommender(params, db)
    logger.info(f"Created recommender: {result}.")
    return result


@router.get("/{id}", response_model=Recommender)
@limiter.limit("10/second")
async def read_recommender(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Recommender:
    logger.info(f"Fetching recommender with id: {id}.")
    result = await recommenders.read_recommender(id, db)
    logger.info(f"Fetched recommender: {result}.")
    return result


@router.get("/", response_model=List[Recommender])
@limiter.limit("10/second")
async def read_recommenders(
    request: Request, db: AsyncSession = Depends(get_db_session)
) -> List[Recommender]:
    logger.info("Fetching recommenders.")
    result = await recommenders.read_recommenders(db)
    logger.info(f"Fetched recommenders: {result}")
    return result


@router.put("/{id}", response_model=Recommender)
@limiter.limit("10/second")
async def update_recommender(
    request: Request,
    id: int,
    params: RecommenderUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Recommender:
    logger.info(f"Updating recommender with id: {id}.")
    result = await recommenders.update_recommender(id, params, db)
    logger.info(f"Updated recommender: {result}.")
    return result


@router.delete("/{id}", response_model=Recommender)
@limiter.limit("10/second")
async def delete_recommender(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Recommender:
    logger.info(f"Deleting recommender with id: {id}.")
    result = await recommenders.delete_recommender(id, db)
    logger.info(f"Deleted recommender: {result}.")
    return result
