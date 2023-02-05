import json
from typing import Any, AsyncIterator, List, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
)

from ....common.types import JsonDumpFunction
from ....custom.sqlalchemy.models import OutboxCustomModel
from ...common.sqlalchemy.storage import AsyncSQLAlchemyStorageMixin
from ..types import AsyncCustomOutboxStorageABC, CustomMessage


class AsyncSQLAlchemyCustomOutboxStorage(
    AsyncCustomOutboxStorageABC,
    AsyncSQLAlchemyStorageMixin,
):

    model = OutboxCustomModel

    def __init__(
        self,
        engine: AsyncEngine,
        json_dump: Optional[JsonDumpFunction] = None,
        scoped_session: Optional[async_scoped_session] = None,
    ) -> None:
        self.engine: AsyncEngine = engine
        self.json_dump: JsonDumpFunction = json_dump or json.dumps
        self.scoped_session: Optional[async_scoped_session] = scoped_session

    def serialize(self, value: str) -> Optional[bytes]:
        if value is None:
            return value
        return self.json_dump(value).encode()

    async def save(
        self,
        value: Any,
        session: Optional[AsyncSession] = None,
        connection: Optional[AsyncConnection] = None,
    ) -> None:
        _value = self.serialize(value)

        connection = await self.get_connection(
            session=session,
            connection=connection,
        )

        await connection.execute(sa.insert(self.model).values(value=_value))

    async def get_messages_batch(self, size: int) -> AsyncIterator[List[CustomMessage]]:

        query = self.model.consume_query(size=size)

        # Create connection to database
        connection: AsyncConnection
        async with self.engine.connect() as connection:

            # get new messages from table forever
            while True:

                # for every batch create new transaction
                async with connection.begin():
                    result = await connection.execute(query)
                    rows = result.fetchall()
                    yield [
                        CustomMessage(
                            id=row["id"],
                            value=row["value"],
                        )
                        for row in rows
                    ]
