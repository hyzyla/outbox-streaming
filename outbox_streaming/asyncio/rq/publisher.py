import asyncio
import logging
import time

import rq
from redis.client import Redis

from .types import AsyncRQOutboxStorageABC

logger = logging.getLogger("outbox-streaming")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class AsyncOutboxRQPublisher:
    def __init__(
        self,
        storage: AsyncRQOutboxStorageABC,
        batch_size: int = 100,
    ) -> None:
        self.storage = storage
        self.batch_size = batch_size
        self.redis = Redis()
        self.queue = rq.Queue(connection=self.redis)

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
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.run_sync)

    async def run_sync(self) -> None:
        logger.debug("Starting outbox publisher")

        async for batch in self.storage.get_tasks_batch(size=self.batch_size):

            logger.debug(f"Publishing outbox tasks: {len(batch)}")
            for task in batch:
                self.queue.enqueue(
                    task.func,
                    *task.args,
                    **task.kwargs,
                )

            # sleep one second between empty batches
            if not batch:
                time.sleep(1)
