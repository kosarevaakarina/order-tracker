import os
from email.message import EmailMessage
from dotenv import load_dotenv
import aiosmtplib
from fastapi import HTTPException
from config.logger import logger
from models.orders import Order

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    async def send_email(self, to_email: str, subject: str, message: str, logger_msg: str):
        """Отправка email."""
        msg = EmailMessage()
        msg["From"] = self.smtp_username
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(message)
        try:
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password
            )
            logger.info(logger_msg)
        except Exception as e:
            logger.error(f"SMTP Error: Notification sending error: {e}")
            raise HTTPException(status_code=500, detail="Error sending email")

    async def notify_order_status_update(self, to_email: str, order_data: Order, previous_status: str):
        """Отправка уведомления об обновлении статуса заказа."""
        subject = f"Обновление статуса заказа ID{order_data.id}"
        message = f"Статус заказа изменился с {previous_status} на {order_data.status}"
        logger_msg = f"Notification of order status change for ID={order_data.id} sent"
        await self.send_email(to_email=to_email, subject=subject, message=message, logger_msg=logger_msg)

    async def notify_order_creation(self, to_email: str, order_data: Order):
        """Отправка уведомления о создании нового заказа."""
        subject = f"Создан новый заказ {order_data.id}"
        message = f"Создан новый заказ. Идентификационный номер: ID{order_data.id}"
        logger_msg = f"Notification of order creation for ID={order_data.id} sent"
        await self.send_email(to_email=to_email, subject=subject, message=message, logger_msg=logger_msg)


