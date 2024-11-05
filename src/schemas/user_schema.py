from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserInfo(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserInfo):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class AccessToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'