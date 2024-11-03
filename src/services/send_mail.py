import os
from email.message import EmailMessage
from dotenv import load_dotenv
import aiosmtplib
from fastapi import HTTPException

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    async def send_email(self, to_email: str, subject: str, message: str):
        """Асинхронный метод для отправки email."""
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
        except Exception as e:
            print(f"Ошибка отправки email: {e}")
            raise HTTPException(status_code=500, detail="Error sending email")

    async def notify_order_status_update(self, to_email, order_data, previous_status):
        """Отправка уведомления об обновлении статуса заказа."""
        subject = f"Обновление статуса заказа ID{order_data.id}"
        message = f"Статус заказа изменился с {previous_status} на {order_data.status}"
        await self.send_email(to_email=to_email, subject=subject, message=message)

    async def notify_order_creation(self, to_email, order_data):
        """Отправка уведомления о создании нового заказа."""
        subject = f"Создан новый заказ {order_data.id}"
        message = f"Создан новый заказ. Идентификационный номер: ID{order_data.id}"
        await self.send_email(to_email=to_email, subject=subject, message=message)



