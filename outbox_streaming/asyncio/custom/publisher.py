from __future__ import annotations

import asyncio
import logging

from ...custom.types import CustomMessage
from .types import AsyncCustomOutboxStorageABC

logger = logging.getLogger("outbox-streaming")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class AsyncOutboxCustomPublisher:
    def __init__(
        self,
        storage: AsyncCustomOutboxStorageABC,
        batch_size: int = 100,
    ) -> None:
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
        logger.debug("Starting outbox publisher")

        async for batch in self.storage.get_messages_batch(size=self.batch_size):

            logger.debug(f"Publishing outbox messages: {len(batch)}")
            for message in batch:
                await self.process_message(message=message)

            # sleep one second between empty batches
            if not batch:
                await asyncio.sleep(1)

    async def process_message(self, message: CustomMessage) -> None:
        """Override this method to process message"""
        pass
