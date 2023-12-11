from kafka import KafkaProducer
import time


class NewProducer:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers="localhost:9092")
        self.topic = "gpt-cost"

    def send(self, message: str):
        self.producer.send(
            topic=self.topic,
            key=f"message_{time.time()}",
            value=message,
            partition=0
        )