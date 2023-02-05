from abc import ABC
from typing import AsyncIterator

from ...custom.types import CustomMessage


class AsyncCustomOutboxStorageABC(ABC):
    def get_messages_batch(self, size: int) -> AsyncIterator[list[CustomMessage]]:
        ...
