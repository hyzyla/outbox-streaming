from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any, Iterator


class CeleryOutboxStorageABC(ABC):
    def get_tasks_batch(self, size: int) -> Iterator[list[CeleryTask]]:
        ...


@dataclass
class CeleryTask:
    id: int
    name: str
    args: list[Any] | None
    kwargs: dict[str, Any] | None
    options: dict[str, Any] | None
