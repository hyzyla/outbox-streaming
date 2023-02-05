from typing import Any, AsyncIterator, Iterable, List, Mapping, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
)

from ..types import AsyncRQOutboxStorageABC, RQMessage
from ...common.sqlalchemy.storage import AsyncSQLAlchemyStorageMixin
from ....rq.sqlalchemy.models import OutboxRQModel


class AsyncSQLAlchemyRQOutboxStorage(
    AsyncRQOutboxStorageABC,
    AsyncSQLAlchemyStorageMixin,
):

    model = OutboxRQModel

    def __init__(
        self,
        engine: AsyncEngine,
        scoped_session: Optional[async_scoped_session] = None,
    ) -> None:
        self.engine: AsyncEngine = engine
        self.scoped_session: Optional[async_scoped_session] = scoped_session

    async def get_connection(
        self,
        session: Optional[AsyncSession] = None,
        connection: Optional[AsyncConnection] = None,
    ) -> AsyncConnection:
        if connection is not None:
            return connection
        if session is not None:
            return await session.connection()
        if self.scoped_session is not None:
            return await self.scoped_session().connection()
        raise TypeError("Can not get connection")

    async def save(
        self,
        func: str,
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        *,
        session: Optional[AsyncSession] = None,
        connection: Optional[AsyncConnection] = None,
    ) -> None:
        """Serialize and save to database RQ task"""

        connection = await self.get_connection(
            session=session,
            connection=connection,
        )

        await connection.execute(
            sa.insert(self.model).values(
                func=func,
                args=args,
                kwargs=kwargs,
            )
        )

    async def get_tasks_batch(self, size: int) -> AsyncIterator[List[RQMessage]]:

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
                        RQMessage(
                            id=row["id"],
                            func=row["func"],
                            args=row["args"],
                            kwargs=row["kwargs"],
                        )
                        for row in rows
                    ]
