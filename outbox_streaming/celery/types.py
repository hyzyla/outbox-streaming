from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional


class CeleryOutboxStorageABC(ABC):
    def get_tasks_batch(self, size: int) -> Iterator[List[CeleryTask]]:
        ...


@dataclass
class CeleryTask:
    id: int
    name: str
    args: Optional[List[Any]]
    kwargs: Optional[Dict[str, Any]]
    options: Optional[Dict[str, Any]]
