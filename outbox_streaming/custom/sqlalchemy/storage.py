import json
from typing import Any, Iterator

import sqlalchemy as sa
import sqlalchemy.orm

from ...common.sqlachemy.storage import SQLAlchemyStorageMixin
from ...common.types import JsonDumpFunction
from ..types import CustomMessage, CustomOutboxStorageABC
from .models import OutboxCustomModel


class SQLAlchemyCustomOutboxStorage(CustomOutboxStorageABC, SQLAlchemyStorageMixin):

    model = OutboxCustomModel

    def __init__(
        self,
        engine: sa.engine.Engine,
        json_dump: JsonDumpFunction | None = None,
        scoped_session: sa.orm.scoped_session | None = None,
    ) -> None:
        self.engine: sa.engine.Engine = engine
        self.json_dump: JsonDumpFunction = json_dump or json.dumps
        self.scoped_session: sa.orm.scoped_session | None = scoped_session

    def serialize(self, value: str) -> bytes | None:
        if value is None:
            return value
        if isinstance(value, bytes):
            return value
        return self.json_dump(value).encode()

    def save(
        self,
        value: Any,
        session: sa.orm.Session | None = None,
        connection: sa.engine.Connection | None = None,
    ) -> None:
        """Serialize and save to database custom message"""
        _value = self.serialize(value)

        connection = self.get_connection(
            session=session,
            connection=connection,
        )

        connection.execute(sa.insert(self.model).values(value=_value))

    def get_messages_batch(self, size: int) -> Iterator[list[CustomMessage]]:

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
                        CustomMessage(
                            id=row["id"],
                            value=row["value"],
                        )
                        for row in rows
                    ]
