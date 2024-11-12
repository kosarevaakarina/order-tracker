import json
from typing import Annotated, List
from fastapi import Depends, APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession
from auth.oauth2 import oauth2_schema, get_user_by_token
from config.db import get_session
from config.logger import logger
from crud.order_crud import OrderCrud
from exceptions import JSONSerializationError, PermissionDeniedException, OrderNotFoundException
from schemas.order_schema import OrderCreate, OrderUpdateStatus, OrderInfo, OrderChangeStatus
from services.kafka.producers import produce_orders

router = APIRouter()

@router.post("/create/", response_model=OrderCreate)
async def create_order(
    access_token: Annotated[str, Depends(oauth2_schema)],
    order_data: OrderCreate = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """Создание заказа"""
    current_user = await get_user_by_token(access_token, session)
    try:
        produce_data = json.dumps({
            "type": "create",
            "order_data": order_data.model_dump(),
            "user_id": current_user.id,
        })
        await produce_orders(data_json=produce_data)
    except Exception as e:
        logger.error(f"JSON serialization error: {e}")
        JSONSerializationError(e)
    return order_data


@router.get("/", response_model=List[OrderInfo])
async def get_orders(
        access_token: Annotated[str, Depends(oauth2_schema)],
        session: AsyncSession = Depends(get_session)
):
    """Просмотр заказов, пользователь может просматривать только свои заказы а суперпользователь все"""
    current_user = await get_user_by_token(access_token, session)
    orders = await OrderCrud.get_all_orders(session, current_user)
    logger.info("User ID=%s retrieved the order list", current_user.id)
    return [OrderInfo.model_validate(order) for order in orders]


@router.put("/{order_id}/", response_model=OrderChangeStatus)
async def update_status_order(
    access_token: Annotated[str, Depends(oauth2_schema)],
    order_id: int,
    order_data: OrderUpdateStatus = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """Изменение статуса заказа"""
    current_user = await get_user_by_token(access_token, session)
    previous_status = order_data.status
    order = await OrderCrud.get_order(order_id, session)
    if not (current_user.is_superuser or current_user.id == order.user_id):
        logger.error("FORBIDDEN: Insufficient permissions to change the status of order ID=%s for user ID=%s", order.id,
                     current_user.id)
        raise PermissionDeniedException()
    if not order:
        raise OrderNotFoundException(order_id)
    if order.status == previous_status:
        logger.warning("Conflict: Failed to change the status for order ID=%s", order_id)
    try:
        notification = json.dumps({
            "type": "update",
            "user_id": current_user.id,
            "order_data": {"id": order_id, "status": order_data.status},
            "previous_status": previous_status
        })
        await produce_orders(data_json=notification)
    except Exception as e:
        logger.error(f"JSON serialization error: {e}")
        JSONSerializationError(e)
    return OrderChangeStatus(id=order_id, status=order_data.status)
