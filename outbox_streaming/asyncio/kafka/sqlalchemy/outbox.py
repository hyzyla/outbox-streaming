from typing import Any, List, Optional

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

    async def save(
        self,
        topic: str,
        value: Any,
        key: Optional[str] = None,
        session: Optional[AsyncSession] = None,
        connection: Optional[AsyncConnection] = None,
    ) -> None:
        return await self.storage.save(
            topic=topic,
            value=value,
            key=key,
            session=session,
            connection=connection,
        )
