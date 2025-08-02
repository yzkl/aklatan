from fastapi import APIRouter

from . import authors, books, recommenders

base_router = APIRouter()

base_router.include_router(authors.router, prefix="/v1", tags=["Authors"])
base_router.include_router(books.router, prefix="/v1", tags=["Books"])
base_router.include_router(recommenders.router, prefix="/v1", tags=["Recommenders"])
