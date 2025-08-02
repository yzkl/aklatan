from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Book(Base):
    __tablename__ = "fct_books"

    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True, nullable=False
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("dim_authors.id"))
    recommender_id: Mapped[int] = mapped_column(ForeignKey("dim_recommenders.id"))
    title: Mapped[str] = mapped_column(String(64))
    year_published: Mapped[int] = mapped_column(Integer)
    is_purchased: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    is_read: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    author = relationship("Author", back_populates="books")
    recommender = relationship("Recommender", back_populates="books")
