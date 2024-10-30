from typing import Annotated
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from config.db import get_session
from crud.order_crud import OrdersCrud
from schemas.orders import OrderCreate, OrderUpdateStatus

order_router = APIRouter()

@order_router.post("create/")
async def create_order(
        order_data: Annotated[OrderCreate, Depends()],
        session: AsyncSession = Depends(get_session)
):
    await OrdersCrud.create_order(order_data, session)
    return order_data


@order_router.get("/")
async def get_orders(session: AsyncSession = Depends(get_session)):
    orders = await OrdersCrud.get_all_orders(session)
    return orders


@order_router.put("/{order_id}/")
async def update_order(
    order_id: int,
    order_data: Annotated[OrderUpdateStatus, Depends()],
    session: AsyncSession = Depends(get_session)
):
    order = await OrdersCrud().update_status_order(session, order_id, order_data)
    return order