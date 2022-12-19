"""Kafka Consumer Module"""
import multiprocessing as mp
import time
from os import environ
from typing import List

from confluent_kafka import Consumer, KafkaError, KafkaException
from confluent_kafka.admin import AdminClient
from models.job import Job
from sqlalchemy import create_engine, event, insert, select, update
from sqlalchemy.orm import Session

from config import Config

conf = {
    "bootstrap.servers": environ["KAFKA_CLUSTER_HOST"],
    "group.id": "foo",
    "auto.offset.reset": "smallest",
    "receive.message.max.bytes": environ["KAFKA_CLUSTER_MAX_BYTES"],
}

admin_client = AdminClient({"bootstrap.servers": environ["KAFKA_CLUSTER_HOST"]})


RUNNING = True
engine = create_engine(
    f"postgresql+psycopg2://{environ['SQLALCHEMY_DATABASE_URI']}",
    echo=False,
    future=True,
)
session = Session(engine, expire_on_commit=False)


def check_topic(topic: str) -> bool:
    """Check topic"""
    return any(
        kafka_topic == topic for kafka_topic in admin_client.list_topics().topics
    )


def update_job_status(job_id: str, status: str):
    """Update the status of a Job"""
    stmt = update(Job).where(Job.job_id == job_id).values(status=status)

    session.execute(stmt)
    session.commit()
    print(f"Job {job_id} is {status}")


def update_job_psi_time(job_id: str, psi_time: str):
    """Update the psi time of a Job"""
    stmt = update(Job).where(Job.job_id == job_id).values(psi=psi_time)

    session.execute(stmt)
    session.commit()


def consume_loop(
    consumer: Consumer, topics: List[str], user_id: str, job_id: str
) -> None:
    """Consumer loop function"""

    try:
        consumer.subscribe(topics)

        while RUNNING:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue

            # pylint: disable=W0212
            if message.error() and message.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(
                    f"{message.topic()} [{message.partition()}] \
                        reached end at offset {message.offset()}"
                )
            elif message.error():
                raise KafkaException(message.error())
            else:
                with open(
                    f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_output", "wb"
                ) as f:
                    f.write(bytes(message.value()))

                print(message.headers()[0])
                _, value = message.headers()[0]
                update_job_psi_time(job_id, value.decode("UTF-8"))

                update_job_status(job_id, "DONE")

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


def loop(job: Job) -> None:
    """Process loop"""
    consumer = Consumer(conf)
    topic_exists = False
    topic = f"{job.org_id}.{job.user_id}.{job.job_id}"

    print(f"Wait for {topic} topic creation")

    while not topic_exists:
        topic_exists = check_topic(topic)
        time.sleep(0.5)

    consume_loop(consumer, [topic], job.user_id, job.job_id)


def populate_queue(limit: int) -> List[str]:
    """Return the Jobs in QUEUED state"""
    queue = []
    stmt = select(Job).where(Job.status.in_(["PENDING"])).limit(limit)

    for job in session.scalars(stmt):
        session.expunge(job)
        update_job_status(job.job_id, "QUEUED")
        queue.append(job)

    return queue


def main() -> None:
    """Fetcher Program"""
    Config()

    QUEUE_MAX_SIZE = 2
    queue = populate_queue(QUEUE_MAX_SIZE)

    print("Fetcher initialized...")
    while True:
        if len(queue) == 0:
            # Get values from DB
            time.sleep(10)
            queue = populate_queue(QUEUE_MAX_SIZE)
        else:
            # Initialize consumer
            ctx = mp.get_context("spawn")
            p = ctx.Process(target=loop, args=(queue.pop(),))
            p.start()


if __name__ == "__main__":
    main()
