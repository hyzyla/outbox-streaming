from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterator, List, Optional


@dataclass
class KafkaMessage:
    id: int
    topic: str
    value: bytes
    key: Optional[str]


class KafkaOutboxStorageABC(ABC):
    def get_messages_batch(self, size: int) -> Iterator[List[KafkaMessage]]:
        ...
