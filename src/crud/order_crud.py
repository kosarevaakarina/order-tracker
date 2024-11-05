from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.logger import logger
from exceptions import PermissionDeniedException, OrderNotFoundException
from models.orders import Order
from models.users import User
from schemas.order_schema import OrderCreate, OrderUpdateStatus


class OrderCrud:
    @staticmethod
    async def create_order(order_data: OrderCreate, current_user: User, session: AsyncSession):
        new_order = Order(
            title=order_data.title,
            description=order_data.description,
            status=order_data.status,
            user_id=current_user.id
        )
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)
        return new_order

    @staticmethod
    async def get_all_orders(session: AsyncSession, user_id: int = None):
        if user_id:
            result = await session.execute(select(Order).where(Order.user_id == user_id))
        else:
            result = await session.execute(select(Order))
        orders = result.scalars().all()
        return orders

    @staticmethod
    async def get_order(order_id: int, session: AsyncSession):
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()
        return order

    @staticmethod
    async def update_status_order(session: AsyncSession, order_data: OrderUpdateStatus, current_user: User):
        order = await OrderCrud.get_order(order_data.id, session)
        if not (current_user.is_superuser or current_user.id == order.user_id):
            logger.error("FORBIDDEN: Insufficient permissions to change the status of order ID=%s for user ID=%s", order.id, current_user.id)
            raise PermissionDeniedException()
        if order.status == order_data.status:
            logger.warning("Conflict: Failed to change the status for order ID=%s", order_data.id)
            raise HTTPException(status_code=409, detail="Conflict: status not changed")
        if order:
            order.status = order_data.status
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order
        else:
            raise OrderNotFoundException(order_data.id)