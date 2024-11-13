import pytest
from unittest import mock
from fastapi import HTTPException
from services.send_mail import EmailService


@pytest.mark.asyncio
class TestSendMail:

    @pytest.fixture
    def email_service(self):
        return EmailService()

    async def test_notify_order_status_update_success(self, email_service):
        with mock.patch.object(email_service, 'send_email', return_value=None) as mock_send_email:
            order_data = {"id": 123, "status": "Shipped"}
            previous_status = "Pending"
            to_email = "test@example.com"
            type = 'update'
            await email_service.notify_order_status_update(to_email, order_data, previous_status, type)
            mock_send_email.assert_called_once_with(
                to_email=to_email,
                subject="Обновление статуса заказа ID=123",
                message="Статус заказа изменился с Pending на Shipped",
                logger_msg="Notification of order status change for ID=123 sent"
            )

    async def test_notify_order_creation_success(self, email_service):
        with mock.patch.object(email_service, 'send_email', return_value=None) as mock_send_email:
            order_id = 123
            to_email = "test@example.com"
            type = 'create'
            await email_service.notify_order_creation(to_email, order_id, type)
            mock_send_email.assert_called_once_with(
                to_email=to_email,
                subject="Создан новый заказ 123",
                message="Создан новый заказ. Идентификационный номер: ID=123",
                logger_msg="Notification of order creation for ID=123 sent"
            )

    async def test_send_email_failure(self, email_service):
        with mock.patch("aiosmtplib.send", side_effect=Exception("SMTP Error")) as mock_send:
            to_email = "test@example.com"
            subject = "Test Subject"
            message = "Test Message"
            logger_msg = "Test Logger Message"
            with pytest.raises(HTTPException):
                await email_service.send_email(to_email, subject, message, logger_msg)
            mock_send.assert_called_once()
