from abc import ABC
from typing import AsyncIterator, List

from ...kafka.types import KafkaMessage


class AsyncKafkaOutboxStorageABC(ABC):
    def get_messages_batch(self, size: int) -> AsyncIterator[List[KafkaMessage]]:
        ...
