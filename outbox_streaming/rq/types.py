from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterator, List, Any


@dataclass
class RQMessage:
    id: int
    func: str
    args: list[Any]
    kwargs: dict[str, Any]


class RQOutboxStorageABC(ABC):
    def get_messages_batch(self, size: int) -> Iterator[List[RQMessage]]:
        ...
