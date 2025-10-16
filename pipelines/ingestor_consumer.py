# consume from news.raw and prices.raw
import json
import os

from confluent_kafka import Consumer
from dotenv import load_dotenv, find_dotenv


# Set up our consumer
load_dotenv(find_dotenv())
consumer_config = {
    "bootstrap.servers": os.getenv("KAFKA_BROKER_HOST", "localhost:9092"),
    "group.id": "ingestor_group",  # Unique group ID for the consumer group
    "auto.offset.reset": "earliest",    # Start reading at the earliest message if no offset is committed
}

consumer = Consumer(consumer_config)

consumer.subscribe(["news.raw"])    # add prices.raw when ready

print("🟢 Consumer is running and subscribed to news.raw")

try:
    while True:
        # Read messages from the topic every second
        msg = consumer.poll(1.0)  # Timeout of 1 second

        if msg is None:
            continue
        if msg.error():
            print(f"❌ Consumer error: {msg.error()}")
            continue

        # Process the message
        message_value = msg.value().decode("utf-8")
        message = json.loads(message_value)
        print(f"✅ Consumed message: {message}")
except KeyboardInterrupt:
    print("🛑 Consumer is shutting down...")
finally:
    consumer.close()
    print("🔴 Consumer has been closed.")