from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, validator


class UserInfo(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserInfo):
    password: str

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов')
        if not any(char.isupper() for char in value):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(char.islower() for char in value):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not any(char.isdigit() for char in value):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return value


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class AccessToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'