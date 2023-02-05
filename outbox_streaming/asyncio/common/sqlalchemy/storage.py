from typing import Type

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
)

from ....common.sqlachemy.base import OutboxMixin


class AsyncSQLAlchemyStorageMixin:

    scoped_session: async_scoped_session | None
    model: Type[OutboxMixin]
    engine: AsyncEngine

    async def get_connection(
        self,
        session: AsyncSession | None = None,
        connection: AsyncConnection | None = None,
    ) -> AsyncConnection:
        if connection is not None:
            return connection
        if session is not None:
            return await session.connection()
        if self.scoped_session is not None:
            return await self.scoped_session().connection()
        raise TypeError("Can not get connection")

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(self.model.metadata.create_all)
