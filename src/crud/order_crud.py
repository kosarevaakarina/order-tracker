from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import PermissionDeniedException
from models.orders import Order
from models.users import User
from schemas.order_schema import OrderCreate, OrderUpdateStatus


class OrdersCrud:
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

    async def get_order(self, order_id: int, session: AsyncSession):
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()
        return order

    async def update_status_order(self, session: AsyncSession, order_data: OrderUpdateStatus, current_user: User):
        order =  await self.get_order(order_data.id, session)
        if not (current_user.is_superuser or current_user.id == order.user_id):
            raise PermissionDeniedException()
        if order:
            order.status = order_data.status
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order