from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterator, List


@dataclass
class CustomMessage:
    id: int
    value: dict[str, str]


class CustomOutboxStorageABC(ABC):
    def get_messages_batch(self, size: int) -> Iterator[List[CustomMessage]]:
        ...
