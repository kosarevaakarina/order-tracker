import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP')
loop = asyncio.get_event_loop()