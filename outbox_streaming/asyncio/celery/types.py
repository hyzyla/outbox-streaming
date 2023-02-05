from __future__ import annotations

from abc import ABC
from typing import AsyncIterator

from ...celery.types import CeleryTask


class AsyncCeleryOutboxStorageABC(ABC):
    def get_tasks_batch(self, size: int) -> AsyncIterator[list[CeleryTask]]:
        ...
