from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    picture_url: str | None = None

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
