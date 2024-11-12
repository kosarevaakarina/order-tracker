from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.orders import Order
from models.users import User


class OrderCrud:
    @staticmethod
    async def create_order(order_data: dict, current_user: User, session: AsyncSession):
        """Создание записи о заказе в БД"""
        new_order = Order(
            title=order_data.get("title"),
            description=order_data.get("description"),
            status=order_data.get("status"),
            price=order_data.get("price"),
            user_id=current_user.id
        )
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)
        return new_order

    @staticmethod
    async def get_all_orders(session: AsyncSession, current_user: User):
        """Получение всех заказов из БД: суперпользователь получает все записи, а обычный пользователь - только свои"""
        if current_user.is_superuser:
            result = await session.execute(select(Order))
        else:
            result = await session.execute(select(Order).where(Order.user_id == current_user.id))
        orders = result.scalars().all()
        return orders

    @staticmethod
    async def get_order(order_id: int, session: AsyncSession):
        """Получение конкретного заказа"""
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()
        return order

    @staticmethod
    async def update_status_order(session: AsyncSession, order_id: int, order_data: dict):
        """Обновление статуса заказа"""
        order = await OrderCrud.get_order(order_id, session)
        order.status = order_data.get("status")
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order