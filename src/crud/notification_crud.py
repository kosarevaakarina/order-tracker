from sqlalchemy.ext.asyncio import AsyncSession
from models.notifications import Notification
from schemas.notification_schema import NotificationCreate


class NotificationCrud:
    @staticmethod
    async def create_notification(session: AsyncSession, notification_data: NotificationCreate):
        new_notification = Notification(
            order_id=notification_data.order_id,
            type=notification_data.type,
            message=notification_data.message
        )
        session.add(new_notification)
        await session.commit()
        await session.refresh(new_notification)