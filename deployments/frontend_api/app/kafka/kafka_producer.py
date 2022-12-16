"""Kafka producer"""
import socket
import time
from os import environ

from confluent_kafka import Producer


class KafkaProducer:
    """Define properties of a kafka producer"""

    def __init__(self):
        self.conf = {
            "bootstrap.servers": environ["KAFKA_CLUSTER_HOST"],
            "message.max.bytes": environ["KAFKA_CLUSTER_MAX_BYTES"],
            "client.id": socket.gethostname(),
        }
        self.start_time = None
        self.producer = Producer(self.conf)
        self.producer.poll(0)

    def acked(self, err, msg):
        """Acknowledge that a meessge was received"""
        if err is not None:
            print(f"Failed to deliver message: {msg}: {err}")

        print(f"Produce {time.time() - self.start_time} seconds")

    def produce(self, headers, data):
        """Produce message"""
        self.start_time = time.time()

        self.producer.produce(
            environ["KAFKA_CLUSTER_INBOUND_TOPIC"],
            key=None,
            value=data,
            on_delivery=self.acked,
            headers=headers,
        )

        self.producer.flush()
