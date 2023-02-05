from typing import Any, Iterable, Mapping

import sqlalchemy as sa
import sqlalchemy.orm
from celery import Celery, Task
from sqlalchemy.ext.asyncio import AsyncEngine, async_scoped_session

from ..publisher import AsyncOutboxCeleryPublisher
from .storage import AsyncSQLAlchemyCeleryOutboxStorage


class AsyncSQLAlchemyCeleryOutbox:

    storage_class = AsyncSQLAlchemyCeleryOutboxStorage
    publisher_class = AsyncOutboxCeleryPublisher

    def __init__(
        self,
        celery: Celery,
        engine: AsyncEngine,
        scoped_session: async_scoped_session | None = None,
    ) -> None:
        self.storage = self.storage_class(engine=engine, scoped_session=scoped_session)
        self.publisher = self.publisher_class(
            celery=celery,
            storage=self.storage,
        )

    async def save(
        self,
        task: Task,
        args: Iterable[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        options: Mapping[str, Any] | None = None,
        session: sa.orm.Session | None = None,
        connection: sa.engine.Connection | None = None,
    ) -> None:
        return await self.storage.save(
            task=task,
            args=args,
            kwargs=kwargs,
            options=options,
            session=session,
            connection=connection,
        )
