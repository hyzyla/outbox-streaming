import asyncio
import logging
import time

from celery import Celery
from celery.result import AsyncResult

from .types import AsyncCeleryOutboxStorageABC

logger = logging.getLogger("outbox-streaming")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class AsyncOutboxKafkaPublisher:
    def __init__(
        self,
        celery: Celery,
        storage: AsyncCeleryOutboxStorageABC,
        batch_size: int = 100,
    ) -> None:
        self.celery = celery
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
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.run_sync)

    async def run_sync(self) -> None:
        logger.debug("Starting outbox publisher")

        async for batch in self.storage.get_tasks_batch(size=self.batch_size):

            logger.debug(f"Publishing outbox tasks: {len(batch)}")
            for task in batch:
                result: AsyncResult = self.celery.send_task(
                    name=task.name,
                    args=task.args,
                    kwarg=task.kwargs,
                    options=task.options,
                )
                result.get()  # wait until task will be sent

            # sleep one second between empty batches
            if not batch:
                time.sleep(1)
