import logging
import threading
import time

from celery import Celery
from celery.result import AsyncResult

from .types import CeleryOutboxStorageABC

logger = logging.getLogger("outbox-streaming")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class OutboxKafkaPublisher:
    def __init__(
        self,
        *,
        app: Celery,
        storage: CeleryOutboxStorageABC,
        batch_size: int = 100,
    ) -> None:
        self.app = app
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
        logger.debug("Starting outbox publisher")

        for batch in self.storage.get_tasks_batch(size=self.batch_size):

            logger.debug(f"Publishing outbox tasks: {len(batch)}")
            for task in batch:
                result: AsyncResult = self.app.send_task(
                    name=task.name,
                    args=task.args,
                    kwarg=task.kwargs,
                    options=task.options,
                )
                result.get()  # wait until task will be sent

            # sleep one second between empty batches
            if not batch:
                time.sleep(1)
