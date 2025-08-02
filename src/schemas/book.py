from typing import Optional

from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    author_id: int
    recommender_id: int
    title: str
    year_published: int
    is_purchased: Optional[bool] = None
    is_read: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True, strict=True)


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    author_id: Optional[int] = None
    recommender_id: Optional[int] = None
    title: Optional[str] = None
    year_published: Optional[int] = None


class Book(BookBase):
    id: int
