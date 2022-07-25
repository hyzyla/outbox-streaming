from __future__ import annotations

import asyncio
import logging
from typing import List

from aiokafka import AIOKafkaProducer

from .types import AsyncKafkaOutboxStorageABC

logger = logging.getLogger("outbox-streaming")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class AsyncOutboxKafkaPublisher:
    def __init__(
        self,
        kafka_servers: List[str],
        storage: AsyncKafkaOutboxStorageABC,
        batch_size: int = 100,
    ) -> None:
        self.kafka_servers: List[str] = kafka_servers
        self.storage = storage
        self.batch_size = batch_size

    def run_background_task(self) -> asyncio.Task[None]:
        task = asyncio.create_task(self._run_auto_restart())
        return task

    async def _run_auto_restart(self) -> None:
        while True:
            try:
                await self.run()
            except Exception as exc:
                logger.error(f"Outbox producer receive exception: {exc}")
                await asyncio.sleep(1)

    async def run(self) -> None:
        # Connect to Kafka server
        producer = AIOKafkaProducer(bootstrap_servers=self.kafka_servers)
        try:
            await self._publish_messages(producer=producer)
        finally:
            await producer.stop()

    async def _publish_messages(self, producer: AIOKafkaProducer) -> None:
        logger.debug("Starting outbox publisher")

        async for batch in self.storage.get_messages_batch(size=self.batch_size):

            logger.debug(f"Publishing outbox messages: {len(batch)}")
            for message in batch:
                await producer.send_and_wait(
                    topic=message.topic,
                    value=message.value,
                    key=message.key,
                )

            # sleep one second between empty batches
            if not batch:
                await asyncio.sleep(1)
