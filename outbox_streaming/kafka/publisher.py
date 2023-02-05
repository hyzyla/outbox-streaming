import logging
import threading
import time

from kafka import KafkaProducer

from .types import KafkaOutboxStorageABC

logger = logging.getLogger("outbox-streaming")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class OutboxKafkaPublisher:
    def __init__(
        self,
        kafka_servers: list[str],
        storage: KafkaOutboxStorageABC,
        batch_size: int = 100,
    ) -> None:
        self.kafka_servers: list[str] = kafka_servers
        self.storage = storage
        self.batch_size = batch_size

    def run_daemon(self) -> threading.Thread:
        """Start sending records in outbox table in background"""
        thread = threading.Thread(target=self._run_auto_restart, daemon=True)
        thread.start()
        return thread

    def _run_auto_restart(self) -> None:
        while True:
            try:
                self.run()
            except Exception as exc:
                logger.error(f"Outbox producer receive exception: {exc}")
                time.sleep(1)

    def run(self) -> None:
        # Connect to Kafka server
        producer = KafkaProducer(bootstrap_servers=self.kafka_servers)
        try:
            self._publish_messages(producer=producer)
        finally:
            producer.close()

    def _publish_messages(self, producer: KafkaProducer) -> None:
        logger.debug("Starting outbox publisher")

        for batch in self.storage.get_messages_batch(size=self.batch_size):

            logger.debug(f"Publishing outbox messages: {len(batch)}")
            for message in batch:
                record = producer.send(
                    topic=message.topic,
                    value=message.value,
                    key=message.key,
                )
                record.get()  # wait until message will be sent

            # sleep one second between empty batches
            if not batch:
                time.sleep(1)
