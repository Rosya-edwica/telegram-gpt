from kafka import KafkaProducer
import time


class NewProducer:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers="localhost:9092")
        self.topic = "gpt-cost"

    def send(self, message: str, partition: int = 0):
        self.producer.send(
            self.topic,
            message.encode("utf-8"),
            partition=partition
        )