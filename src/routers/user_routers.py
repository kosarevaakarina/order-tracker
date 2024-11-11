from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Annotated, List
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from auth.hash_password import HashPassword
from auth.oauth2 import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_schema, get_user_by_token
from config.db import get_session
from config.logger import logger
from crud.user_crud import UserCrud
from exceptions import UserNotFoundException
from schemas.user_schema import UserInfo, UserCreate, UserUpdate, AccessToken
from services.check_permissions import check_permissions_users

router = APIRouter()


@router.get('/', response_model=List[UserInfo])
async def get_all_users(
    access_token: Annotated[str, Depends(oauth2_schema)],
    session: AsyncSession = Depends(get_session)
):
    """Получение всех пользователей, доступно для суперпользователя"""
    current_user = await get_user_by_token(access_token, session)
    check_permissions_users(current_user, superuser_only=True)
    users = await UserCrud.get_users(session)
    logger.info("Retrieving the list of users by user ID=%s", current_user.id)
    return [UserInfo.model_validate(user) for user in users]


@router.get('/{user_id}', response_model=UserInfo)
async def get_user_detail(
    access_token: Annotated[str, Depends(oauth2_schema)],
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Получение информации о пользователе, доступно пользователю и суперпользователю"""
    user = await UserCrud.get_user(session, user_id)
    if not user:
        logger.error("Not found: User with ID=%s not exist", user_id)
        raise UserNotFoundException()
    current_user = await get_user_by_token(access_token, session)
    check_permissions_users(current_user, user_id=user.id)
    logger.info("Retrieving information about user ID=%s by user ID=%s", user.id, current_user.id)
    return user


@router.post('/register', response_model=UserInfo)
async def register(
    request: UserCreate = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """Регистрация пользователя """
    user = await UserCrud.create_user(session, request)
    logger.info("A new user registered with ID=%s", user.id)
    return user


@router.put('/{user_id}/update', response_model=UserInfo)
async def update_user(
    user_id: int,
    access_token: Annotated[str, Depends(oauth2_schema)],
    request: UserUpdate = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """Обновление иноформации о пользователе, доступно пользователю и суперпользователю"""
    user = await UserCrud.get_user(session, user_id)
    if not user:
        logger.error("Not found: User with ID=%s not exist", user_id)
        raise UserNotFoundException()
    current_user = await get_user_by_token(access_token, session)
    check_permissions_users(current_user, user_id=user.id)
    update_user = await UserCrud.update_user(session, request=request, user_id=user_id)
    logger.info("Information for user ID=%s updated by user ID=%s", user.id, current_user.id)
    return update_user


@router.delete('/{user_id}/delete', response_model=UserInfo)
async def delete_user(
        user_id: int,
        access_token: Annotated[str, Depends(oauth2_schema)],
        session: AsyncSession = Depends(get_session)
):
    """Удаление пользователя, доступно пользователю и суперпользователю"""
    user = await UserCrud.get_user(session, user_id=user_id)
    if not user:
        logger.error("Not found: User with ID=%s not exist", user_id)
        raise UserNotFoundException()
    current_user = await get_user_by_token(access_token, session)
    check_permissions_users(current_user, superuser_only=True)
    logger.info("User ID=%s deleted by user ID=%s", user.id, current_user.id)
    return await UserCrud.delete_user(session, user_id)


@router.post("/token", response_model=AccessToken)
async def login(
        request: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session),
):
    """Авторизация пользователя"""
    user = await UserCrud.get_user(session, username=request.username)
    if not user:
        logger.error("Not found: User with username='%s' not exist", request.username)
        raise UserNotFoundException()
    if not HashPassword.verify(user.hashed_password, request.password):
        logger.error("User with username='%s' entered an incorrect password", request.username)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid password')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"username": user.username}, expires_delta=access_token_expires)
    logger.info("User with username=%s has logged in", request.username)
    token = AccessToken(access_token=access_token)
    return token