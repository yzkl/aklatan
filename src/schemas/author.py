from pydantic import BaseModel, ConfigDict


class AuthorBase(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True, strict=True)


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int
