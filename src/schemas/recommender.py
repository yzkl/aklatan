from pydantic import BaseModel, ConfigDict


class RecommenderBase(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True, strict=True)


class RecommenderCreate(RecommenderBase):
    pass


class RecommenderUpdate(RecommenderBase):
    pass


class Recommender(RecommenderBase):
    id: int
