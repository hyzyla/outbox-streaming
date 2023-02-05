from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterator


@dataclass
class KafkaMessage:
    id: int
    topic: str
    value: bytes
    key: str | None


class KafkaOutboxStorageABC(ABC):
    def get_messages_batch(self, size: int) -> Iterator[list[KafkaMessage]]:
        ...
