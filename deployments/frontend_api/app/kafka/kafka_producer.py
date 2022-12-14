"""Kafka producer"""
import socket
import time
from os import environ

from confluent_kafka import Producer


class KafkaProducer:

    start_time = None

    def __init__(self):
        self.conf = {
            "bootstrap.servers": environ["KAFKA_CLUSTER_HOST"],
            "message.max.bytes": environ["KAFKA_CLUSTER_MAX_BYTES"],
            "client.id": socket.gethostname(),
        }

        self.producer = Producer(self.conf)
        self.producer.poll(0)

    def acked(self, err, msg):
        global start_time

        """Acknowledged"""
        if err is not None:
            print(f"Failed to deliver message: {msg}: {err}")

        print(f"Produce {time.time() - start_time} seconds")

    def produce(self, headers, data):
        """Produce message"""
        global start_time
        start_time = time.time()

        self.producer.produce(
            environ["KAFKA_CLUSTER_INBOUND_TOPIC"],
            key=None,
            value=data,
            on_delivery=self.acked,
            headers=headers,
        )

        self.producer.flush()
