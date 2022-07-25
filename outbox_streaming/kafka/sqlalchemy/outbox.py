from typing import Any, List, Optional

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
        kafka_servers: List[str],
        json_dump: Optional[JsonDumpFunction] = None,
        scoped_session: Optional[sa.orm.scoped_session] = None,
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
        key: Optional[str] = None,
        session: Optional[sa.orm.Session] = None,
        connection: Optional[sa.engine.Connection] = None,
    ) -> None:
        return self.storage.save(
            topic=topic,
            value=value,
            key=key,
            session=session,
            connection=connection,
        )
