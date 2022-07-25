import json
from typing import Any, Iterator, List, Optional

import sqlalchemy as sa
import sqlalchemy.orm

from ...common.sqlachemy.storage import SQLAlchemyStorageMixin
from ...common.types import JsonDumpFunction
from ..types import KafkaMessage, KafkaOutboxStorageABC
from .models import OutboxKafkaModel


class SQLAlchemyKafkaOutboxStorage(KafkaOutboxStorageABC, SQLAlchemyStorageMixin):

    model = OutboxKafkaModel

    def __init__(
        self,
        engine: sa.engine.Engine,
        json_dump: Optional[JsonDumpFunction] = None,
        scoped_session: Optional[sa.orm.scoped_session] = None,
    ) -> None:
        self.engine: sa.engine.Engine = engine
        self.json_dump: JsonDumpFunction = json_dump or json.dumps
        self.scoped_session: Optional[sa.orm.scoped_session] = scoped_session

    def serialize(self, value: str) -> Optional[bytes]:
        if value is None:
            return value
        if isinstance(value, bytes):
            return value
        return self.json_dump(value).encode()

    def save(
        self,
        topic: str,
        value: Any,
        key: Optional[str] = None,
        session: Optional[sa.orm.Session] = None,
        connection: Optional[sa.engine.Connection] = None,
    ) -> None:
        """Serialize and save to database Kafka message"""
        _value = self.serialize(value)

        connection = self.get_connection(
            session=session,
            connection=connection,
        )

        connection.execute(
            sa.insert(self.model).values(
                topic=topic,
                value=_value,
                key=key,
            )
        )

    def get_messages_batch(self, size: int) -> Iterator[List[KafkaMessage]]:

        query = self.model.consume_query(size=size)

        # Create connection to database
        with self.engine.connect() as connection:

            # get new messages from table forever
            while True:

                # for every batch create new transaction
                with connection.begin():
                    result = connection.execute(query)
                    rows = result.fetchall()
                    yield [
                        KafkaMessage(
                            id=row["id"],
                            key=row["key"],
                            topic=row["topic"],
                            value=row["value"],
                        )
                        for row in rows
                    ]
