from aiokafka import AIOKafkaConsumer
import json
from config.db import get_session
from config.logger import logger
from crud.order_crud import OrderCrud
from crud.user_crud import UserCrud
from services.kafka.settings import KAFKA_BOOTSTRAP_SERVERS
from services.send_mail import EmailService


async def consume_orders():
    try:
        consumer = AIOKafkaConsumer(
        'order_topic',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id='group-id'
        )
        await consumer.start()
        try:
            async for msg in consumer:
                order_msg = json.loads(msg.value.decode('utf-8'))
                user_id = order_msg['user_id']
                order_data = order_msg['order_data']
                async for session in get_session():
                    current_user = await UserCrud.get_user(session, user_id=user_id)
                mail_service = EmailService()
                if order_msg['type'] == 'create':
                    order = await OrderCrud.create_order(order_data, current_user, session)
                    logger.info("Order ID=%s created by user ID=%s", order.id, current_user.id)
                    await mail_service.notify_order_creation(
                        to_email=current_user.email,
                        order_id=order.id
                    )
                else:
                    order_id = order_data.get('id')
                    order = await OrderCrud().update_status_order(session, order_id, order_data)
                    logger.info("Order ID=%s status changed by user ID=%s", order_id, current_user.id)
                    await mail_service.notify_order_status_update(
                        to_email=current_user.email,
                        order_data=order_data,
                        previous_status=order_msg['previous_status']
                    )
        except Exception as e:
            logger.error(f"Error in Kafka consumer: {e}")
        finally:
            await consumer.stop()
    except Exception as e:
        logger.error(f"Error in Kafka consumer: {e}")
