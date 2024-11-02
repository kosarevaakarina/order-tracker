from typing import Annotated, List
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.oauth2 import oauth2_schema, get_current_user
from config.db import get_session
from crud.order_crud import OrdersCrud
from exceptions import UserNotFoundException
from schemas.order_schema import OrderCreate, OrderUpdateStatus, OrderInfo

router = APIRouter()

@router.post("create/", response_model=OrderCreate)
async def create_order(
        access_token: Annotated[str, Depends(oauth2_schema)],
        order_data: Annotated[OrderCreate, Depends()],
        session: AsyncSession = Depends(get_session)
):
    """Создание заказа"""
    current_user = await get_current_user(access_token, session)
    if not current_user:
        raise UserNotFoundException()
    await OrdersCrud.create_order(order_data, current_user, session)
    return order_data


@router.get("/", response_model=List[OrderInfo])
async def get_orders(
        access_token: Annotated[str, Depends(oauth2_schema)],
        session: AsyncSession = Depends(get_session)
):
    """Просмотр заказов, пользователь может просматривать только свои заказы а суперпользователь все"""
    current_user = await get_current_user(access_token, session)
    if not current_user:
        raise UserNotFoundException()
    if current_user.is_superuser:
        orders = await OrdersCrud.get_all_orders(session)
    else:
        orders = await OrdersCrud.get_all_orders(session, current_user.id)
    return [OrderInfo.from_orm(order) for order in orders]


@router.put("/{order_id}/", response_model=OrderInfo)
async def update_status_order(
    access_token: Annotated[str, Depends(oauth2_schema)],
    order_data: Annotated[OrderUpdateStatus, Depends()],
    session: AsyncSession = Depends(get_session)
):
    """Изменение статуса заказа"""
    current_user = await get_current_user(access_token, session)
    if not current_user:
        raise UserNotFoundException()
    order = await OrdersCrud().update_status_order(session, order_data, current_user)
    return order