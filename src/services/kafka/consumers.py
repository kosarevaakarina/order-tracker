from aiokafka import AIOKafkaConsumer
import json
from config.logger import logger
from services.kafka.settings import KAFKA_BOOTSTRAP_SERVERS, loop
from services.send_mail import EmailService


async def consume_notification():
    try:
        consumer = AIOKafkaConsumer(
            'order_notifications',
            loop=loop,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id='group-id'
        )
        await consumer.start()
        try:
            async for msg in consumer:
                notification = json.loads(msg.value.decode('utf-8'))
                mail_service = EmailService()
                if notification.get('type') == 'create':
                    await mail_service.notify_order_creation(
                        to_email=notification["user_email"],
                        order_id=notification["order_id"]
                    )
                else:
                    await mail_service.notify_order_status_update(
                        to_email=notification['user_email'],
                        order_data=notification['order_data'],
                        previous_status=notification['previous_status']
                    )
        except Exception as e:
            logger.error(f"Error in Kafka consumer: {e}")
        finally:
            await consumer.stop()
    except Exception as e:
        logger.error(f"Error in Kafka consumer: {e}")
