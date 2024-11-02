from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, List
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.hash_password import HashPassword
from auth.oauth2 import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_schema, get_current_user
from config.db import get_session
from crud.user_crud import UserCrud
from exceptions import PermissionDeniedException, UserNotFoundException
from schemas.user_schema import UserInfo, UserCreate, UserUpdate

router = APIRouter()


@router.get('/', response_model=List[UserInfo])
async def get_all_users(
    access_token: Annotated[str, Depends(oauth2_schema)],
    session: AsyncSession = Depends(get_session)
):
    """Получение всех пользователей, доступно для суперпользователя"""
    current_user = await get_current_user(access_token, session)
    if not current_user.is_superuser:
        raise PermissionDeniedException()
    users = await UserCrud.get_users(session)
    return [UserInfo.from_orm(user) for user in users]


@router.get('/{id}', response_model=UserInfo)
async def get_user_detail(
    access_token: Annotated[str, Depends(oauth2_schema)],
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Получение информации о пользователе, доступно пользователю и суперпользователю"""
    user = await UserCrud.get_user(session, user_id)
    if not user:
        raise UserNotFoundException()
    current_user = await get_current_user(access_token, session)
    if not (current_user.is_superuser or current_user.id == user.id):
        raise PermissionDeniedException()
    return user


@router.post('/register', response_model=UserInfo)
async def register(
    request: Annotated[UserCreate, Depends()],
    session: AsyncSession = Depends(get_session)
):
    """Регистрация пользователя """
    return await UserCrud.create_user(session, request)


@router.put('/{id}/update', response_model=UserInfo)
async def update_user(
    user_id: int,
    access_token: Annotated[str, Depends(oauth2_schema)],
    request: Annotated[UserUpdate, Depends()],
    session: AsyncSession = Depends(get_session)
):
    """Обновление иноформации о пользователе, доступно пользователю и суперпользователю"""
    user = await UserCrud.get_user(session, user_id)
    if not user:
        raise UserNotFoundException()
    current_user = await get_current_user(access_token, session)
    if not (current_user.is_superuser or current_user.id == user.id):
        raise PermissionDeniedException()
    update_user = await UserCrud.update_user(session, request=request, user_id=user_id)
    return update_user


@router.delete('/{id}/delete', response_model=UserInfo)
async def delete_user(
        user_id: int,
        access_token: Annotated[str, Depends(oauth2_schema)],
        session: AsyncSession = Depends(get_session)
):
    """Удаление пользователя, доступно пользователю и суперпользователю"""

    user = await UserCrud.get_user(session, user_id=user_id)
    if not user:
        raise UserNotFoundException()
    current_user = await get_current_user(access_token, session)
    if not current_user.is_superuser:
        raise PermissionDeniedException()
    return await UserCrud.delete_user(session, user_id)


@router.post("/token")
async def login(
        request: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session),
):
    """Авторизация пользователя"""
    user = await UserCrud.get_user(session, username=request.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not HashPassword.verify(user.hashed_password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid password')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"username": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}