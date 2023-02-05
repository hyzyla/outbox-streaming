from typing import Any

import sqlalchemy as sa
import sqlalchemy.orm

from ...common.types import JsonDumpFunction
from ..publisher import OutboxKafkaPublisher
from .storage import SQLAlchemyKafkaOutboxStorage


class SQLAlchemyKafkaOutbox:

    storage_class = SQLAlchemyKafkaOutboxStorage
    publisher_class = OutboxKafkaPublisher

    def __init__(
        self,
        engine: sa.engine.Engine,
        kafka_servers: list[str],
        json_dump: JsonDumpFunction | None = None,
        scoped_session: sa.orm.scoped_session | None = None,
    ) -> None:
        self.storage = self.storage_class(
            engine=engine, json_dump=json_dump, scoped_session=scoped_session
        )
        self.publisher = self.publisher_class(
            kafka_servers=kafka_servers,
            storage=self.storage,
        )

    def save(
        self,
        topic: str,
        value: Any,
        key: str | None = None,
        session: sa.orm.Session | None = None,
        connection: sa.engine.Connection | None = None,
    ) -> None:
        return self.storage.save(
            topic=topic,
            value=value,
            key=key,
            session=session,
            connection=connection,
        )
