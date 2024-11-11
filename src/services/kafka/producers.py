from aiokafka import AIOKafkaProducer

from services.kafka.settings import loop, KAFKA_BOOTSTRAP_SERVERS


async def produce_notification(data_json):
    topic = 'order_notifications'
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        await producer.send_and_wait(topic=topic, value=data_json.encode('utf-8'))
    except Exception as e:
        print(e)
    finally:
        await producer.stop()