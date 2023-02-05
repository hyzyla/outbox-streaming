import logging
import threading
import time

from .types import CustomMessage, CustomOutboxStorageABC

logger = logging.getLogger("outbox-streaming")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class OutboxCustomPublisher:
    def __init__(
        self,
        storage: CustomOutboxStorageABC,
        batch_size: int = 100,
    ) -> None:
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

        for batch in self.storage.get_messages_batch(size=self.batch_size):

            logger.debug(f"Publishing outbox messages: {len(batch)}")
            for message in batch:
                self.process_message(message)

            # sleep one second between empty batches
            if not batch:
                time.sleep(1)

    def process_message(self, message: CustomMessage) -> None:
        """Override this method to process message"""
        pass
