from typing import Annotated, List
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from auth.oauth2 import oauth2_schema, get_user_by_token
from config.db import get_session
from config.logger import logger
from crud.order_crud import OrderCrud
from schemas.order_schema import OrderCreate, OrderUpdateStatus, OrderInfo
from services.send_mail import EmailService

router = APIRouter()

@router.post("create/", response_model=OrderCreate)
async def create_order(
        access_token: Annotated[str, Depends(oauth2_schema)],
        order_data: Annotated[OrderCreate, Depends()],
        session: AsyncSession = Depends(get_session)
):
    """Создание заказа"""
    current_user = await get_user_by_token(access_token, session)
    order = await OrderCrud.create_order(order_data, current_user, session)
    logger.info("Order ID=%s created by user ID=%s", order.id, current_user.id)
    # отправка уведомления на почту о создании нового заказа
    mail_service = EmailService()
    await mail_service.notify_order_creation(
        to_email=current_user.email,
        order_data=order
    )
    return order_data


@router.get("/", response_model=List[OrderInfo])
async def get_orders(
        access_token: Annotated[str, Depends(oauth2_schema)],
        session: AsyncSession = Depends(get_session)
):
    """Просмотр заказов, пользователь может просматривать только свои заказы а суперпользователь все"""
    current_user = await get_user_by_token(access_token, session)
    if current_user.is_superuser:
        orders = await OrderCrud.get_all_orders(session)
    else:
        orders = await OrderCrud.get_all_orders(session, current_user.id)
    logger.info("User ID=%s retrieved the order list", current_user.id)
    return [OrderInfo.from_orm(order) for order in orders]


@router.put("/{order_id}/", response_model=OrderInfo)
async def update_status_order(
    access_token: Annotated[str, Depends(oauth2_schema)],
    order_data: Annotated[OrderUpdateStatus, Depends()],
    session: AsyncSession = Depends(get_session)
):
    """Изменение статуса заказа"""
    current_user = await get_user_by_token(access_token, session)
    previous_status = order_data.status
    order = await OrderCrud().update_status_order(session, order_data, current_user)
    logger.info("Order ID=%s status changed by user ID=%s", order.id, current_user.id)
    # отправка уведомления об изменении статуса заказа на почту
    email_service = EmailService()
    await email_service.notify_order_status_update(
        to_email=current_user.email,
        order_data=order,
        previous_status=previous_status
    )
    return order