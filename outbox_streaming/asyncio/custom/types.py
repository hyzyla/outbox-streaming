from abc import ABC
from typing import AsyncIterator, List

from ...custom.types import CustomMessage


class AsyncCustomOutboxStorageABC(ABC):
    def get_messages_batch(self, size: int) -> AsyncIterator[List[CustomMessage]]:
        ...
