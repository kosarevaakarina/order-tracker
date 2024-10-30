from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.orders import Order, OrderStatus
from schemas.orders import OrderCreate, OrderUpdateStatus


class OrdersCrud:
    @staticmethod
    async def create_order(order_data: OrderCreate, session: AsyncSession):
        new_order = Order(
            title=order_data.title,
            description=order_data.description,
            status=order_data.status,
            user_id=order_data.user_id
        )
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)
        return new_order

    @staticmethod
    async def get_all_orders(session: AsyncSession):
        result = await session.execute(select(Order))
        orders = result.scalars().all()
        return orders

    async def get_order(self, order_id: int, session: AsyncSession):
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()
        return order

    async def update_status_order(self, session: AsyncSession, order_id: int, order_data: OrderUpdateStatus):
        order =  await self.get_order(order_id, session)
        if order:
            order.status = order_data.status
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order

    async def delete_order(self, session: AsyncSession, order_id: int):
        order =  await self.get_order(order_id, session)
        if order:
            await session.delete(order)
            await session.commit()
        return order