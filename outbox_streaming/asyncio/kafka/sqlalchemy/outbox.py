from typing import Any

import sqlalchemy as sa
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession

from ....common.types import JsonDumpFunction
from ..publisher import AsyncOutboxKafkaPublisher
from .storage import AsyncSQLAlchemyKafkaOutboxStorage


class AsyncSQLAlchemyKafkaOutbox:

    storage_class = AsyncSQLAlchemyKafkaOutboxStorage
    publisher_class = AsyncOutboxKafkaPublisher

    def __init__(
        self,
        engine: AsyncEngine,
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

    async def save(
        self,
        topic: str,
        value: Any,
        key: str | None = None,
        session: AsyncSession | None = None,
        connection: AsyncConnection | None = None,
    ) -> None:
        return await self.storage.save(
            topic=topic,
            value=value,
            key=key,
            session=session,
            connection=connection,
        )
