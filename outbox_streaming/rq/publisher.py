import logging
import threading
import time

import rq
from redis.client import Redis

from .types import RQOutboxStorageABC

logger = logging.getLogger("outbox-streaming")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class OutboxRQPublisher:
    def __init__(
        self,
        storage: RQOutboxStorageABC,
        batch_size: int = 100,
    ) -> None:
        self.storage = storage
        self.batch_size = batch_size
        self.redis = Redis()
        self.queue = rq.Queue(connection=self.redis)

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

        for batch in self.storage.get_messages_batch(size=self.batch_size):

            logger.debug(f"Publishing outbox messages: {len(batch)}")
            for message in batch:

                self.queue.enqueue(
                    message.func,
                    *message.args,
                    **message.kwargs,
                )

            # sleep one second between empty batches
            if not batch:
                time.sleep(1)
