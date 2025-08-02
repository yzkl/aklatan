from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Recommender(Base):
    __tablename__ = "dim_recommenders"

    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(64), unique=True)

    books = relationship("Book", back_populates="recommender")
