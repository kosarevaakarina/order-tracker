import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from config.db import get_session
from config.logger import logger
from crud.user_crud import UserCrud
from dotenv import load_dotenv
from exceptions import CredentialException, UserNotFoundException

load_dotenv()

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/v1/api/users/token')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание токена авторизации"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_schema), session: AsyncSession = Depends(get_session)):
    """Получение пользователя по токену авторизации"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        decode_username: str = payload.get('username')
        if decode_username is None:
            raise CredentialException()
    except JWTError:
        raise CredentialException()
    user = await UserCrud.get_user(session, username=decode_username)
    if user is None:
        raise CredentialException()
    return user


async def get_user_by_token(access_token: str, session: AsyncSession):
    """Получение пользователя по токену или выбрасывание исключения, если он не найден"""
    current_user = await get_current_user(access_token, session)
    if not current_user:
        logger.error("Not found: User with token: %s not exist", access_token)
        raise UserNotFoundException()
    return current_user
