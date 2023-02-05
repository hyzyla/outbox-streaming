from __future__ import annotations

from abc import ABC
from typing import AsyncIterator, List

from ...rq.types import RQMessage


class AsyncRQOutboxStorageABC(ABC):
    def get_tasks_batch(self, size: int) -> AsyncIterator[List[RQMessage]]:
        ...
